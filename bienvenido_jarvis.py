#!/usr/bin/env python3
"""
Jarvis — bienvenida al iniciar (inspirado en el asistente de Iron Man, no oficial).

Al ejecutar: voz (Edge TTS), música local opcional, OpenCode + Cursor (Linux).

Dependencias:
    pip install edge-tts pygame psutil requests

Uso:
    python bienvenido_jarvis.py [--dry-run]
    python bienvenido_jarvis.py run [--dry-run]
    python bienvenido_jarvis.py doctor
    python bienvenido_jarvis.py version
    python bienvenido_jarvis.py --doctor
    Variables: env > ~/.config/jarvis-startup/config.json > perfil en código (ver jarvis_config.py).
"""

from __future__ import annotations

import json
import sys

__version__ = "2.3.3"

import argparse
import asyncio
import datetime
import locale as _locale_mod
import os
import shutil
import subprocess
import tempfile
import time

import edge_tts
import psutil
import requests


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


TEXT_ONLY = _truthy_env("JARVIS_TEXT_ONLY")
if not TEXT_ONLY:
    import pygame
else:
    pygame = None  # type: ignore[assignment]

try:
    import jarvis_lista
except ImportError:
    jarvis_lista = None  # type: ignore[misc, assignment]

try:
    from jarvis_config import load_user_config
except ImportError:

    def load_user_config() -> dict:  # type: ignore[misc]
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# Perfiles (JARVIS_PROFILE): defaults por “contexto”; env > ~/.config/.../config.json > PROFILES
# ──────────────────────────────────────────────────────────────────────────────
PROFILES: dict[str, dict[str, str]] = {
    "default": {
        "titulo": "Señor Pulido",
        "project": "~/Desktop/nuevo_proyecto",
    },
    "taller": {
        "titulo": "señor",
        "project": "~/Desktop/nuevo_proyecto",
    },
    "casa": {
        "titulo": "señor",
        "project": "~/Documentos/jarvis-startup",
    },
}

_USER_CONFIG = load_user_config()


def _profile_name() -> str:
    ev = os.getenv("JARVIS_PROFILE", "").strip().lower()
    if ev:
        return ev
    fv = _USER_CONFIG.get("profile")
    if isinstance(fv, str) and fv.strip():
        return fv.strip().lower()
    return "default"


_pd = PROFILES.get(_profile_name(), PROFILES["default"]).copy()


def _pick_setting(env_key: str, file_key: str, profile_val: str, default: str) -> str:
    ev = os.getenv(env_key, "").strip()
    if ev:
        return ev
    fv = _USER_CONFIG.get(file_key)
    if isinstance(fv, str) and fv.strip():
        return fv.strip()
    if profile_val:
        return profile_val
    return default


_TIT_DEFAULT = _pd.get("titulo", "señor")
_PROJ_DEFAULT = _pd.get("project", "~/Desktop/nuevo_proyecto")
TITULO = _pick_setting("JARVIS_TITULO", "titulo", _TIT_DEFAULT, "señor")
NEW_PROJECT = os.path.expanduser(_pick_setting("JARVIS_NEW_PROJECT", "project", _PROJ_DEFAULT, "~/Desktop/nuevo_proyecto"))

_MF_FALLBACK = "~/jarvis-startup/iron_music.mp3"
_mf_raw = _pick_setting("JARVIS_MUSIC_FILE", "music_file", "", "")
MUSIC_FILE = os.path.expanduser((_mf_raw or _MF_FALLBACK).strip() or _MF_FALLBACK)

# Chime opcional estilo HUD (.wav / .ogg); canales distintos al de la voz TTS
BOOT_SOUND_RAW = os.getenv("JARVIS_BOOT_SOUND", "").strip()
CHIME_CHANNEL_INDEX = 1
# Dos canales a 1.0 suman ~+6 dB (más que un solo canal al máximo de pygame)
CHIME_CHANNEL_COUNT = 2

SKIP_NETWORK = os.getenv("JARVIS_SKIP_NETWORK", "").strip().lower() in ("1", "true", "yes", "on")

# iron: tono mayordomo / IA estilo película (español, sin copiar diálogos literales)
# minimal: frases más cortas
JARVIS_THEME = _pick_setting("JARVIS_THEME", "theme", "iron", "iron").strip().lower()

JARVIS_TTS_VOICE = os.getenv("JARVIS_TTS_VOICE", "es-ES-AlvaroNeural").strip()
JARVIS_TTS_RATE = os.getenv("JARVIS_TTS_RATE", "+0%").strip()
if not JARVIS_TTS_RATE.startswith(("+", "-")):
    JARVIS_TTS_RATE = "+0%"


def _ui_lang() -> str:
    """Idea 90: idioma UI (es/en) vía JARVIS_LANG o prefijo de LANG."""
    j = os.getenv("JARVIS_LANG", "").strip().lower()[:2]
    if j in ("en", "es"):
        return j
    lang = os.getenv("LANG", "")
    if lang.lower().startswith("en"):
        return "en"
    return "es"


_STRINGS: dict[str, dict[str, str]] = {
    "es": {
        "seq_start": "\n🚀  Iniciando secuencia de bienvenida…\n",
        "seq_done": "\n✅  Secuencia completada.\n",
        "dry_run": "  [dry-run] Sin chime, TTS, música ni lanzar aplicaciones.\n",
        "readme": "  📄  Abriendo README del proyecto.",
        "pdf": "  📑  Abriendo documentos PDF configurados.",
        "shot": "  📷  Captura de pantalla guardada (consentimiento explícito).",
        "hud": "  📟  HUD en esquina (cierra la ventana para quitar).",
        "notify_start": "Sesión de taller iniciada.",
    },
    "en": {
        "seq_start": "\n🚀  Starting welcome sequence…\n",
        "seq_done": "\n✅  Sequence complete.\n",
        "dry_run": "  [dry-run] No chime, TTS, music, or launching apps.\n",
        "readme": "  📄  Opening project README.",
        "pdf": "  📑  Opening configured PDF documents.",
        "shot": "  📷  Screenshot saved (explicit consent).",
        "hud": "  📟  HUD corner window (close it to dismiss).",
        "notify_start": "Workshop session started.",
    },
}


def _tr(key: str) -> str:
    lang = _ui_lang()
    return _STRINGS.get(lang, _STRINGS["es"]).get(key, _STRINGS["es"].get(key, key))


def _tts_voice_effective() -> str:
    """Idea 8: voz Edge según JARVIS_TTS_VOICE o auto según LANG."""
    if _truthy_env("JARVIS_TTS_AUTO_LANG"):
        lang = (os.getenv("LANG") or "").lower()
        if lang.startswith("en"):
            return os.getenv("JARVIS_TTS_VOICE_EN", "en-US-GuyNeural").strip()
        return os.getenv("JARVIS_TTS_VOICE_ES", "es-ES-AlvaroNeural").strip()
    return JARVIS_TTS_VOICE

VOICE_CHANNEL_INDEX = 0
# Por defecto ~3x el volumen histórico (0.4375); pygame máx 1.0
MUSIC_VOLUME = min(1.0, float(os.getenv("JARVIS_MUSIC_VOLUME", "1.0")))

# Retrasos entre pasos (segundos)
DELAY_AFTER_OPENCODE = float(os.getenv("JARVIS_DELAY_OPENCODE", "1.2"))
DELAY_AFTER_CURSOR = float(os.getenv("JARVIS_DELAY_CURSOR", "1.2"))
DELAY_BEFORE_WMCTRL = float(os.getenv("JARVIS_DELAY_WMCTRL", "5.0"))

NO_NOTIFY = os.getenv("JARVIS_NO_NOTIFY", "").strip().lower() in ("1", "true", "yes", "on")

# Simulación sin TTS / audio / abrir apps (también env JARVIS_DRY_RUN)
DRY_RUN = os.getenv("JARVIS_DRY_RUN", "").strip().lower() in ("1", "true", "yes", "on")

# Mencionar hostname en saludo (estilo “unidad de cómputo”)
USE_HOSTNAME = os.getenv("JARVIS_USE_HOSTNAME", "1").strip().lower() not in (
    "0",
    "false",
    "no",
    "off",
)

# Texto de batería si hay BAT* (escritorio sin batería → cadena vacía)
USE_BATTERY = os.getenv("JARVIS_USE_BATTERY", "1").strip().lower() not in (
    "0",
    "false",
    "no",
    "off",
)

# Log de última ejecución
LAST_RUN_PATH = os.path.expanduser("~/.local/share/jarvis-startup/last_run.json")
SKIP_LAST_RUN_LOG = os.getenv("JARVIS_SKIP_LAST_RUN_LOG", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

# Sin clima/red externa en saludo, sin hostname/batería; frases más cortas (pantalla compartida)
PRIVACY_MODE = os.getenv("JARVIS_PRIVACY_MODE", "").strip().lower() in ("1", "true", "yes", "on")

# Segundo chime al abrir IDE (tras Cursor)
IDE_CHIME_RAW = os.getenv("JARVIS_IDE_CHIME", "").strip()

# Fade música (ms); 0 desactiva
def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


MUSIC_FADE_IN_MS = max(0, _env_int("JARVIS_MUSIC_FADE_IN_MS", 1200))
MUSIC_FADEOUT_MS = max(0, _env_int("JARVIS_MUSIC_FADEOUT_MS", 1200))

# HUD en ventana aparte (tkinter); por defecto desactivado
HUD_ENABLED = os.getenv("JARVIS_HUD", "").strip().lower() in ("1", "true", "yes", "on")

# Diagnósticos extra en el texto del saludo (no en modo privacidad)
DIAG_DISK = os.getenv("JARVIS_DIAG_DISK", "").strip().lower() in ("1", "true", "yes", "on")
DIAG_GIT = os.getenv("JARVIS_DIAG_GIT", "").strip().lower() in ("1", "true", "yes", "on")

# Lista 1–100: anexos y matices (ver jarvis_lista.py)
LISTA_COMPLETA = os.getenv("JARVIS_LISTA_COMPLETA", "").strip().lower() in ("1", "true", "yes", "on")
FOCUS_MODE = os.getenv("JARVIS_FOCUS", "").strip().lower() in ("1", "true", "yes", "on")
EXPO_MODE = os.getenv("JARVIS_EXPO", "").strip().lower() in ("1", "true", "yes", "on")
SKIP_AMBIENT_AUDIO = FOCUS_MODE or EXPO_MODE or TEXT_ONLY


def _git_workspace() -> str:
    g = os.getenv("JARVIS_GIT_DIR", "").strip()
    return os.path.expanduser(g) if g else NEW_PROJECT


def _texto_diag_disco() -> str:
    if PRIVACY_MODE or not DIAG_DISK:
        return ""
    try:
        home = os.path.expanduser("~")
        u = shutil.disk_usage(home)
        if not u.total:
            return ""
        pct = int(100 * (u.used / u.total))
        return f"Almacenamiento del taller al {pct} por ciento de uso."
    except OSError:
        return ""


def _texto_diag_git() -> str:
    if PRIVACY_MODE or not DIAG_GIT:
        return ""
    root = _git_workspace()
    if not os.path.isdir(os.path.join(root, ".git")):
        return ""
    try:
        br = subprocess.run(
            ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        st = subprocess.run(
            ["git", "-C", root, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if br.returncode != 0:
            return ""
        branch = (br.stdout or "").strip() or "?"
        dirty = bool((st.stdout or "").strip())
        estado = "con cambios pendientes" if dirty else "limpio"
        return f"Repositorio en rama {branch}, {estado}."
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _append_frases_diag(texto: str) -> str:
    partes = [p for p in (_texto_diag_disco(), _texto_diag_git()) if p]
    if not partes:
        return texto
    return f"{texto.rstrip()} {' '.join(partes)}"


def _finalizar_saludo(line1: str, line2: str) -> tuple[str, str]:
    """Aplica ideas de lista (jarvis_lista) y diagnósticos disco/git."""
    l1, l2 = line1, line2
    if jarvis_lista:
        l1, l2 = jarvis_lista.enhance_lines(
            l1,
            l2,
            privacy=PRIVACY_MODE,
            lista_completa=LISTA_COMPLETA,
            titulo=TITULO,
            theme=JARVIS_THEME,
        )
        if EXPO_MODE and not PRIVACY_MODE and len(l2) > 240:
            l2 = l2[:237] + "..."
    l2 = _append_frases_diag(l2)
    if jarvis_lista and LISTA_COMPLETA and not PRIVACY_MODE:
        ax = jarvis_lista.build_saludo_annex(
            privacy=PRIVACY_MODE,
            lista_completa=True,
            new_project=NEW_PROJECT,
        )
        if ax:
            l2 = f"{l2.rstrip()} {ax}"
    return l1, l2


def _launch_hud_overlay(dry_run: bool) -> bool:
    """Arranca HUD en proceso hijo. Devuelve True si se lanzó."""
    if dry_run or not HUD_ENABLED:
        return False
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hud_overlay.py")
    if not os.path.isfile(script):
        print("  ⚠️  hud_overlay.py no encontrado.")
        return False
    try:
        subprocess.Popen(
            [sys.executable, script],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(_tr("hud"))
        return True
    except OSError as e:
        print(f"  ⚠️  No se pudo iniciar el HUD (¿python3-tk?): {e}")
        return False


def _hostname_corto() -> str:
    try:
        import socket

        return socket.gethostname().split(".")[0]
    except OSError:
        return ""


def _session_is_wayland() -> bool:
    return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" or bool(
        os.environ.get("WAYLAND_DISPLAY", "").strip()
    )


def _texto_bateria() -> str:
    if PRIVACY_MODE or not USE_BATTERY:
        return ""
    base = "/sys/class/power_supply"
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return ""
    for name in names:
        if not name.startswith("BAT"):
            continue
        cap = os.path.join(base, name, "capacity")
        try:
            with open(cap, encoding="utf-8") as f:
                pct = f.read().strip()
            if pct.isdigit():
                return f"Energía del reactor al {pct} por ciento."
        except OSError:
            continue
    return ""


def _escribir_last_run(ok: bool, dry_run: bool, extra: dict | None = None) -> None:
    if SKIP_LAST_RUN_LOG:
        return
    payload = {
        "version": __version__,
        "ok": ok,
        "dry_run": dry_run,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if extra:
        payload.update(extra)
    try:
        os.makedirs(os.path.dirname(LAST_RUN_PATH), exist_ok=True)
        with open(LAST_RUN_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _ensure_mixer() -> None:
    if pygame is None:
        return
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    pygame.mixer.set_num_channels(32)


def reproducir_chime_opcional() -> None:
    """Un sonido corto al inicio (opcional); no usa mixer.music."""
    if pygame is None:
        return
    if not BOOT_SOUND_RAW:
        return
    path = os.path.expanduser(BOOT_SOUND_RAW)
    if not os.path.isfile(path):
        print(f"  ⚠️  JARVIS_BOOT_SOUND no encontrado: {path}")
        return
    try:
        _ensure_mixer()
        snd = pygame.mixer.Sound(path)
        snd.set_volume(1.0)
        canales: list[pygame.mixer.Channel] = []
        for i in range(CHIME_CHANNEL_COUNT):
            c = pygame.mixer.Channel(CHIME_CHANNEL_INDEX + i)
            c.set_volume(1.0)
            c.play(snd)
            canales.append(c)
        while any(c.get_busy() for c in canales):
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"  ⚠️  No se pudo reproducir el chime: {e}")


def reproducir_chime_ide_opcional() -> None:
    """Chime opcional tras abrir Cursor (fase ‘taller’). Canales 3–4 para no solapar boot."""
    if pygame is None:
        return
    if SKIP_AMBIENT_AUDIO:
        return
    if not IDE_CHIME_RAW:
        return
    path = os.path.expanduser(IDE_CHIME_RAW)
    if not os.path.isfile(path):
        print(f"  ⚠️  JARVIS_IDE_CHIME no encontrado: {path}")
        return
    base = CHIME_CHANNEL_INDEX + CHIME_CHANNEL_COUNT
    try:
        _ensure_mixer()
        snd = pygame.mixer.Sound(path)
        snd.set_volume(1.0)
        canales: list[pygame.mixer.Channel] = []
        for i in range(CHIME_CHANNEL_COUNT):
            c = pygame.mixer.Channel(base + i)
            c.set_volume(1.0)
            c.play(snd)
            canales.append(c)
        while any(c.get_busy() for c in canales):
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"  ⚠️  No se pudo reproducir el chime del IDE: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Clima y saludo (tema Iron Man vs minimal)
# ──────────────────────────────────────────────────────────────────────────────
def obtener_clima() -> str:
    if SKIP_NETWORK or PRIVACY_MODE:
        return ""
    for intento in range(2):
        try:
            r = requests.get("https://wttr.in/?lang=es&format=%t+con+cielo+%C", timeout=4)
            if r.status_code == 200:
                return " La temperatura externa es de " + r.text.replace("+", " ") + "."
        except requests.RequestException:
            if intento == 0:
                time.sleep(0.4)
    return ""


def _maybe_play_scan_sound(dry_run: bool) -> None:
    """Idea 20: sonido muy breve al leer métricas (opcional)."""
    if dry_run or pygame is None or SKIP_AMBIENT_AUDIO:
        return
    raw = os.getenv("JARVIS_SCAN_SOUND", "").strip()
    if not raw:
        return
    path = os.path.expanduser(raw)
    if not os.path.isfile(path):
        return
    try:
        _ensure_mixer()
        snd = pygame.mixer.Sound(path)
        snd.set_volume(0.12)
        ch = pygame.mixer.Channel(5)
        ch.play(snd)
    except Exception:
        pass


def obtener_saludo_dinamico(dry_run: bool = False) -> tuple[str, str]:
    _maybe_play_scan_sound(dry_run)
    ahora = datetime.datetime.now()
    hora = ahora.hour
    hora_actual = ahora.strftime("%H:%M")
    clima_str = "" if dry_run else obtener_clima()
    bat_str = _texto_bateria()
    host_str = ""
    if USE_HOSTNAME and not PRIVACY_MODE:
        hn = _hostname_corto()
        if hn:
            host_str = f" Unidad «{hn}»."

    cpu_p = int(psutil.cpu_percent(interval=0.5))
    mem_p = int(psutil.virtual_memory().percent)

    if PRIVACY_MODE:
        if JARVIS_THEME == "minimal":
            if 5 <= hora < 12:
                saludo = "Buenos días"
            elif 12 <= hora < 20:
                saludo = "Buenas tardes"
            else:
                saludo = "Buenas noches"
            return _finalizar_saludo(
                f"{saludo}, {TITULO}. Son las {hora_actual}.",
                f"CPU al {cpu_p} por ciento, memoria al {mem_p} por ciento. Entorno listo.",
            )
        if 5 <= hora < 12:
            saludo = "Buenos días"
        elif 12 <= hora < 20:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"
        return _finalizar_saludo(
            f"{saludo}, {TITULO}. Son las {hora_actual}. Sistemas listos. ¿Seguimos?",
            f"Diagnóstico local: CPU al {cpu_p} por ciento, memoria al {mem_p} por ciento. Abriendo entorno.",
        )

    if JARVIS_THEME == "minimal":
        if 5 <= hora < 12:
            saludo = "Buenos días"
        elif 12 <= hora < 20:
            saludo = "Buenas tardes"
        else:
            saludo = "Buenas noches"
        sufijo_sys = " ".join(
            s.strip()
            for s in (clima_str.strip(), bat_str)
            if s and s.strip()
        )
        if sufijo_sys:
            sufijo_sys = sufijo_sys + " "
        line_b = f"{sufijo_sys}CPU al {cpu_p} por ciento, memoria al {mem_p} por ciento. Abriendo entorno de trabajo."
        return _finalizar_saludo(
            f"{saludo}, {TITULO}. Son las {hora_actual}.{host_str}",
            line_b,
        )

    # Tema "iron": mayordomo digital, tono de la película (sin citas literales)
    if 5 <= hora < 12:
        saludo = "Buenos días"
        linea_extra = "Bienvenido al taller. "
    elif 12 <= hora < 20:
        saludo = "Buenas tardes"
        linea_extra = "Sistemas en línea. "
    else:
        saludo = "Buenas noches"
        linea_extra = "Bienvenido a casa. "

    linea1 = f"{saludo}, {TITULO}. Son las {hora_actual}. {linea_extra}¿En qué trabajamos hoy?{host_str}"
    prefijo = " ".join(
        s.strip()
        for s in (clima_str.strip(), bat_str)
        if s and s.strip()
    )
    if prefijo:
        prefijo = prefijo + " "
    linea2 = (
        f"{prefijo}Diagnóstico: CPU al {cpu_p} por ciento, memoria al {mem_p} por ciento. "
        f"Todo dentro de parámetros. Preparando su entorno de desarrollo."
    )
    return _finalizar_saludo(linea1, linea2)


def _print_banner_optional() -> None:
    bf = os.getenv("JARVIS_BANNER_FILE", "").strip()
    if bf:
        p = os.path.expanduser(bf)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    print(fh.read().rstrip() + "\n")
            except OSError:
                pass
            return
    btxt = os.getenv("JARVIS_ANSI_BANNER", "").strip()
    if btxt:
        print(btxt + "\n")


def _maybe_open_readme(dry_run: bool) -> None:
    if dry_run or not _truthy_env("JARVIS_OPEN_README"):
        return
    base = os.path.dirname(os.path.abspath(__file__))
    readme = os.path.join(base, "README.md")
    if not os.path.isfile(readme):
        return
    xdg = shutil.which("xdg-open")
    if not xdg:
        return
    try:
        subprocess.Popen([xdg, readme], start_new_session=True)
        print(_tr("readme"))
    except OSError:
        pass


def _reproducir_chime_env(var_name: str, dry_run: bool) -> None:
    if dry_run or pygame is None or SKIP_AMBIENT_AUDIO:
        return
    raw = os.getenv(var_name, "").strip()
    if not raw:
        return
    path = os.path.expanduser(raw)
    if not os.path.isfile(path):
        return
    try:
        _ensure_mixer()
        snd = pygame.mixer.Sound(path)
        snd.set_volume(0.45)
        pygame.mixer.Channel(6).play(snd)
    except pygame.error:
        pass


def _notify_session_start(dry_run: bool) -> None:
    """Idea 1: notificación opcional al inicio (tema / sesión)."""
    if dry_run or NO_NOTIFY:
        return
    if not _truthy_env("JARVIS_NOTIFY_START"):
        return
    if subprocess.run(["which", "notify-send"], capture_output=True).returncode != 0:
        return
    try:
        titulo = "Jarvis"
        cuerpo = f"{_tr('notify_start')} ({JARVIS_THEME})"
        subprocess.run(
            ["notify-send", "-a", "Jarvis", titulo, cuerpo],
            capture_output=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        pass


def _maybe_open_pdfs(dry_run: bool) -> None:
    """Idea 74: rutas PDF separadas por : o coma; xdg-open."""
    raw = os.getenv("JARVIS_PDF_PATHS", "").strip()
    if not raw or dry_run:
        return
    xdg = shutil.which("xdg-open")
    if not xdg:
        return
    sep = ":" if ":" in raw else ","
    opened = 0
    for part in raw.split(sep):
        p = os.path.expanduser(part.strip())
        if p.lower().endswith(".pdf") and os.path.isfile(p):
            try:
                subprocess.Popen([xdg, p], start_new_session=True)
                opened += 1
            except OSError:
                pass
    if opened:
        print(_tr("pdf"))


def _maybe_screenshot(dry_run: bool) -> None:
    """Idea 31: captura opt-in con consentimiento explícito."""
    if dry_run or not _truthy_env("JARVIS_SCREENSHOT_CONSENT"):
        return
    tool = None
    for t in ("grim", "scrot", "gnome-screenshot"):
        if shutil.which(t):
            tool = t
            break
    if not tool:
        return
    base = os.path.expanduser(
        os.getenv("JARVIS_SCREENSHOT_DIR", "~/.local/share/jarvis-startup/screenshots")
    )
    try:
        os.makedirs(base, exist_ok=True)
    except OSError:
        return
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base, f"jarvis_{ts}.png")
    try:
        if tool == "grim":
            subprocess.run(["grim", path], check=False, timeout=15, capture_output=True)
        elif tool == "scrot":
            subprocess.run(["scrot", path], check=False, timeout=15, capture_output=True)
        else:
            subprocess.run(
                ["gnome-screenshot", "-f", path],
                check=False,
                timeout=15,
                capture_output=True,
            )
        if os.path.isfile(path):
            print(_tr("shot"))
    except (OSError, subprocess.TimeoutExpired):
        pass


def secuencia_bienvenida(dry_run: bool = False) -> None:
    print(_tr("seq_start"))
    _notify_session_start(dry_run=dry_run)
    op = os.getenv("JARVIS_OPENING_PHRASE", "").strip()
    if op:
        print(f"  {op}\n")
    _print_banner_optional()
    if dry_run:
        print(_tr("dry_run"))

    if jarvis_lista:
        jarvis_lista.maybe_jitter_startup()

    if not dry_run and not SKIP_AMBIENT_AUDIO:
        _ensure_mixer()
        reproducir_chime_opcional()

    mensajes = obtener_saludo_dinamico(dry_run=dry_run)

    hablar(mensajes[0], dry_run=dry_run)
    preparar_y_reproducir_musica(dry_run=dry_run)
    hablar(mensajes[1], dry_run=dry_run)
    abrir_apps_lado_a_lado(dry_run=dry_run)

    print(_tr("seq_done"))
    closing = os.getenv("JARVIS_CLOSING_PHRASE", "").strip()
    if closing:
        print(f"  {closing}")
        if _truthy_env("JARVIS_CLOSING_TTS") and not dry_run:
            hablar(closing, dry_run=False)
    if not dry_run:
        try:
            if pygame is not None and MUSIC_FADEOUT_MS > 0 and pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(MUSIC_FADEOUT_MS)
                fin = time.time() + (MUSIC_FADEOUT_MS / 1000.0) + 0.6
                while pygame.mixer.music.get_busy() and time.time() < fin:
                    pygame.time.Clock().tick(30)
            elif pygame is not None:
                pygame.mixer.music.stop()
        except pygame.error:
            pass
    _reproducir_chime_env("JARVIS_CHIME_SUCCESS", dry_run)
    _maybe_open_readme(dry_run)
    _maybe_open_pdfs(dry_run)
    _maybe_screenshot(dry_run)
    notificar_escritorio(dry_run=dry_run)
    hud_ok = _launch_hud_overlay(dry_run=dry_run)
    extra_run: dict = {
        "hostname": _hostname_corto(),
        "theme": JARVIS_THEME,
        "privacy_mode": PRIVACY_MODE,
        "wayland": _session_is_wayland(),
        "hud_launched": hud_ok,
        "lista_completa": LISTA_COMPLETA,
    }
    _escribir_last_run(True, dry_run, extra_run)
    if jarvis_lista:
        jarvis_lista.run_hooks(dry_run=dry_run)
        jarvis_lista.write_session_report(extra_run)


async def generar_audio_edge(texto: str, archivo: str) -> None:
    communicate = edge_tts.Communicate(texto, _tts_voice_effective(), rate=JARVIS_TTS_RATE)
    await communicate.save(archivo)


def _hablar_espeak(texto: str) -> bool:
    for exe in ("espeak-ng", "espeak"):
        bin_path = shutil.which(exe)
        if not bin_path:
            continue
        try:
            subprocess.run(
                [bin_path, "-v", "es", "-s", "155", texto],
                capture_output=True,
                timeout=120,
                check=False,
            )
            return True
        except (OSError, subprocess.TimeoutExpired):
            continue
    return False


def hablar(texto: str, dry_run: bool = False) -> None:
    print(f"  🔊  Diciendo: «{texto}»")
    if dry_run:
        print("  [dry-run] TTS omitido.")
        return
    if TEXT_ONLY:
        if _hablar_espeak(texto):
            print("  🔊  Modo texto: espeak (sin pygame).")
        else:
            print("  ⚠️  Modo texto: instale espeak-ng para voz local o desactive JARVIS_TEXT_ONLY.")
        return
    fd, tts_path = tempfile.mkstemp(suffix=".mp3", prefix="jarvis_tts_")
    os.close(fd)
    try:
        asyncio.run(generar_audio_edge(texto, tts_path))

        _ensure_mixer()
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.set_volume(max(0.1, MUSIC_VOLUME * 0.5))
        except pygame.error:
            pass

        voz = pygame.mixer.Sound(tts_path)
        canal = pygame.mixer.Channel(VOICE_CHANNEL_INDEX)
        canal.set_volume(1.0)
        canal.play(voz)
        while canal.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"  ❌  Fallo la conexión o el motor edge-tts: {e}")
        if _hablar_espeak(texto):
            print("  🔊  Respaldo: espeak (sin red).")
    finally:
        try:
            if pygame is not None:
                vol = MUSIC_VOLUME * (jarvis_lista.mark_music_volume_factor() if jarvis_lista else 1.0)
                pygame.mixer.music.set_volume(min(1.0, vol))
        except pygame.error:
            pass
        try:
            os.unlink(tts_path)
        except OSError:
            pass


def preparar_y_reproducir_musica(dry_run: bool = False) -> None:
    if pygame is None:
        return
    if dry_run:
        if os.path.exists(MUSIC_FILE):
            print(f"  [dry-run] Se reproduciría música: {MUSIC_FILE}")
        else:
            print(f"  [dry-run] No hay MP3 en {MUSIC_FILE}")
        return
    if SKIP_AMBIENT_AUDIO:
        print("  🔇  Modo foco/expo/texto: sin música de fondo.")
        return
    if os.path.exists(MUSIC_FILE):
        print("  🎵  Iniciando música de fondo de JARVIS...")
        _ensure_mixer()
        pygame.mixer.music.load(MUSIC_FILE)
        vol = MUSIC_VOLUME * (jarvis_lista.mark_music_volume_factor() if jarvis_lista else 1.0)
        pygame.mixer.music.set_volume(min(1.0, vol))
        if MUSIC_FADE_IN_MS > 0:
            pygame.mixer.music.play(loops=-1, fade_ms=MUSIC_FADE_IN_MS)
        else:
            pygame.mixer.music.play(loops=-1)
    else:
        print(f"  ⚠️  Música de fondo no encontrada. Guarda un MP3 en: {MUSIC_FILE}")


def _resolver_ruta_opencode() -> str | None:
    override = os.getenv("JARVIS_OPENCODE_BIN", "").strip()
    if override:
        p = os.path.expanduser(override)
        if os.path.isfile(p):
            return p
    if os.path.isfile("/usr/local/bin/opencode"):
        return "/usr/local/bin/opencode"
    return shutil.which("opencode")


def _resolver_ruta_cursor() -> str | None:
    override = os.getenv("JARVIS_CURSOR_BIN", "").strip()
    if override:
        p = os.path.expanduser(override)
        if os.path.isfile(p):
            return p
    for path in (
        "/usr/share/cursor/bin/cursor",
        "/usr/local/bin/cursor",
        os.path.expanduser("~/.cursor/bin/cursor"),
        "/opt/homebrew/bin/cursor",
    ):
        if os.path.isfile(path):
            return path
    return shutil.which("cursor")


def abrir_apps_lado_a_lado(dry_run: bool = False) -> None:
    if dry_run:
        op = _resolver_ruta_opencode() or "opencode"
        cu = _resolver_ruta_cursor() or "cursor"
        print("  [dry-run] No se lanzan procesos. Equivalente a:")
        print(f"    • terminal + {op}")
        print(f"    • {cu} --new-window {NEW_PROJECT}")
        sec = os.getenv("JARVIS_SECOND_PATH", "").strip()
        if sec:
            print(f"    • segundo proyecto: {cu} --new-window {os.path.expanduser(sec)}")
        print("    • wmctrl (si existe) para mosaico")
        if IDE_CHIME_RAW:
            print(f"    • chime IDE: {os.path.expanduser(IDE_CHIME_RAW)}")
        return
    sw, sh = obtener_resolucion_pantalla()
    mitad = sw // 2
    geom_izq = f"0,0,0,{mitad},{sh}"
    geom_der = f"0,{mitad},0,{mitad},{sh}"

    os.makedirs(NEW_PROJECT, exist_ok=True)

    print("  🤖  Abriendo OpenCode en una nueva terminal...")
    opencode_bin = _resolver_ruta_opencode()
    env_gui = os.environ.copy()
    if opencode_bin and os.path.isfile(opencode_bin):
        subprocess.Popen(
            ["kgx", "--", "bash", "-c", f"{opencode_bin}; exec bash"],
            env=env_gui,
            start_new_session=True,
        )
    else:
        print("  ⚠️  OpenCode no encontrado; intentando genérico...")
        subprocess.Popen(
            ["x-terminal-emulator", "-e", "bash -c 'opencode; exec bash'"],
            env=env_gui,
            start_new_session=True,
        )
    time.sleep(DELAY_AFTER_OPENCODE)

    print("  💻  Abriendo Cursor...")
    cursor_bin = _resolver_ruta_cursor()
    if cursor_bin and os.path.isfile(cursor_bin):
        subprocess.Popen([cursor_bin, "--new-window", NEW_PROJECT], env=env_gui, start_new_session=True)
    else:
        print("  ⚠️  Cursor no encontrado; intentando genérico...")
        subprocess.Popen(["cursor", "--new-window", NEW_PROJECT], env=env_gui, start_new_session=True)
    time.sleep(DELAY_AFTER_CURSOR)

    sec_path = os.getenv("JARVIS_SECOND_PATH", "").strip()
    if sec_path:
        sec_exp = os.path.expanduser(sec_path)
        os.makedirs(sec_exp, exist_ok=True)
        print("  💻  Abriendo segundo proyecto en Cursor...")
        if cursor_bin and os.path.isfile(cursor_bin):
            subprocess.Popen([cursor_bin, "--new-window", sec_exp], env=env_gui, start_new_session=True)
        else:
            subprocess.Popen(["cursor", "--new-window", sec_exp], env=env_gui, start_new_session=True)
        time.sleep(min(1.0, DELAY_AFTER_CURSOR))

    reproducir_chime_ide_opcional()

    if _session_is_wayland():
        print(
            "  ℹ️  Sesión Wayland: wmctrl es para X11; si no mueve ventanas, "
            "use reglas del compositor o sesión Xorg."
        )

    if subprocess.run(["which", "wmctrl"], capture_output=True).returncode == 0:
        print("  🪟  Organizando ventanas con wmctrl...")
        time.sleep(DELAY_BEFORE_WMCTRL)
        subprocess.run(["wmctrl", "-R", "OpenCode", "-e", geom_izq], env=env_gui)
        subprocess.run(["wmctrl", "-R", "Cursor", "-e", geom_der], env=env_gui)
        subprocess.run(["wmctrl", "-R", "Visual Studio Code", "-e", geom_der], env=env_gui)
    else:
        print("  ⚠️  wmctrl no instalado, no se reorganizarán las ventanas")


def obtener_resolucion_pantalla() -> tuple[int, int]:
    try:
        out = subprocess.run(["xrandr"], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if " connected " in line and "+" in line:
                part = line.split(" ")
                for token in part:
                    if "+" in token and "x" in token:
                        res = token.split("+")[0]
                        w, h = res.split("x")
                        return int(w), int(h)
    except Exception:
        pass
    return 1920, 1080


def notificar_escritorio(dry_run: bool = False) -> None:
    if dry_run:
        print("  [dry-run] notify-send omitido.")
        return
    if NO_NOTIFY:
        return
    if subprocess.run(["which", "notify-send"], capture_output=True).returncode != 0:
        return
    titulo = "Jarvis"
    cuerpo = "Secuencia completada. Listo para trabajar, señor."
    if JARVIS_THEME == "minimal":
        cuerpo = "Listo."
    try:
        icon = os.getenv("JARVIS_NOTIFY_ICON", "").strip()
        icon_p = os.path.expanduser(icon) if icon else ""
        cmd = (
            ["notify-send", "-i", icon_p, "-a", "Jarvis", titulo, cuerpo]
            if icon_p and os.path.isfile(icon_p)
            else ["notify-send", "-a", "Jarvis", titulo, cuerpo]
        )
        subprocess.run(
            cmd,
            capture_output=True,
            timeout=5,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass


def mostrar_config(dry_run: bool = False) -> None:
    print("\n⚙️  Configuración actual:")
    print(f"  versión = {__version__}")
    print(f"  dry_run = {dry_run or DRY_RUN}")
    print(f"  JARVIS_THEME = {JARVIS_THEME}")
    print(f"  JARVIS_PROFILE = {os.getenv('JARVIS_PROFILE', 'default')}")
    print(f"  TITULO = {TITULO}")
    print(f"  MUSIC_FILE = {MUSIC_FILE}")
    print(f"  JARVIS_BOOT_SOUND = {BOOT_SOUND_RAW or '(no definido)'}")
    print(f"  JARVIS_IDE_CHIME = {IDE_CHIME_RAW or '(no definido)'}")
    print(f"  JARVIS_PRIVACY_MODE = {PRIVACY_MODE}")
    print(f"  música fade in/out ms = {MUSIC_FADE_IN_MS} / {MUSIC_FADEOUT_MS}")
    print(f"  JARVIS_HUD = {HUD_ENABLED}")
    print(f"  JARVIS_DIAG_DISK / JARVIS_DIAG_GIT = {DIAG_DISK} / {DIAG_GIT}")
    print(
        f"  LISTA_COMPLETA / FOCUS / EXPO / TEXT_ONLY = {LISTA_COMPLETA} / {FOCUS_MODE} / {EXPO_MODE} / {TEXT_ONLY}"
    )
    print(f"  NEW_PROJECT = {NEW_PROJECT}")
    print(f"  TTS = {_tts_voice_effective()} @ {JARVIS_TTS_RATE} (JARVIS_TTS_VOICE={JARVIS_TTS_VOICE})")
    print(f"  JARVIS_USE_HOSTNAME = {USE_HOSTNAME}")
    print(f"  JARVIS_USE_BATTERY = {USE_BATTERY}")
    print(f"  SKIP_NETWORK = {SKIP_NETWORK}")
    print(f"  NO_NOTIFY = {NO_NOTIFY}")
    print(f"  last_run log = {LAST_RUN_PATH} (skip={SKIP_LAST_RUN_LOG})")
    try:
        print(f"  locale = {_locale_mod.getlocale()}")
        lang = os.getenv("LANG", "")
        if lang and "es" not in lang.lower() and JARVIS_TTS_VOICE.startswith("es-"):
            print(
                "  ℹ️  LANG sugiere no-español: puede ajustar JARVIS_TTS_VOICE "
                "(p. ej. en-US-GuyNeural). Ver docs/ENV.md."
            )
    except (OSError, AttributeError):
        pass


def main(dry_run: bool = False) -> None:
    dry = bool(dry_run or DRY_RUN)
    if jarvis_lista:
        if not jarvis_lista.network_ok():
            print("Jarvis: sin conectividad; se aborta (JARVIS_REQUIRE_NETWORK=1).")
            raise SystemExit(0)
        if not jarvis_lista.monitor_likely_on():
            print("Jarvis: sin sesión gráfica detectada; se aborta (JARVIS_REQUIRE_MONITOR=1).")
            raise SystemExit(0)
    mostrar_config(dry_run=dry)
    print("=" * 55)
    print("  Ejecutando bienvenida al iniciar…")
    print("=" * 55)
    try:
        secuencia_bienvenida(dry_run=dry)
    except KeyboardInterrupt:
        _escribir_last_run(False, dry, {"reason": "KeyboardInterrupt"})
        print("\n\nInterrumpido. 👋")
        sys.exit(130)
    except Exception as e:
        _escribir_last_run(False, dry, {"error": str(e)})
        _reproducir_chime_env("JARVIS_CHIME_ERROR", dry)
        raise


def _parse_args(argv: list[str] | None = None) -> tuple[str, argparse.Namespace]:
    """
    Devuelve (comando, namespace). Comandos: run, doctor, version.
    Compatibilidad: sin subcomando se interpreta como run (--dry-run, --doctor, --version).
    """
    raw = list(argv if argv is not None else sys.argv[1:])
    if not raw:
        ns = argparse.Namespace(dry_run=False)
        return ("run", ns)

    if raw[0] == "doctor":
        p = argparse.ArgumentParser(
            prog="jarvis-bienvenida doctor",
            description="Comprueba dependencias y herramientas opcionales.",
        )
        p.parse_args(raw[1:])
        return ("doctor", argparse.Namespace())

    if raw[0] == "version":
        return ("version", argparse.Namespace())

    if raw[0] == "run":
        p = argparse.ArgumentParser(
            prog="jarvis-bienvenida run",
            description="Secuencia de bienvenida (por defecto si no indicas subcomando).",
        )
        p.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula la secuencia sin TTS, música, chime ni abrir aplicaciones",
        )
        ns = p.parse_args(raw[1:])
        return ("run", ns)

    p = argparse.ArgumentParser(
        description="Jarvis: bienvenida por voz y entorno de trabajo (inspiración Iron Man, no oficial). "
        "Subcomandos: run, doctor, version. Sin subcomando: mismo comportamiento que run.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula la secuencia sin TTS, música, chime ni abrir aplicaciones",
    )
    p.add_argument(
        "--doctor",
        action="store_true",
        help="Diagnóstico de entorno (equivalente al subcomando doctor)",
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"jarvis-bienvenida {__version__}",
    )
    ns = p.parse_args(raw)
    if ns.doctor:
        return ("doctor", argparse.Namespace())
    return ("run", ns)


def main_cli(argv: list[str] | None = None) -> None:
    cmd, ns = _parse_args(argv)
    if cmd == "version":
        print(f"jarvis-bienvenida {__version__}")
        raise SystemExit(0)
    if cmd == "doctor":
        import jarvis_doctor

        code = jarvis_doctor.run_doctor_cli(music_file=MUSIC_FILE)
        raise SystemExit(code)
    dry = bool(getattr(ns, "dry_run", False))
    main(dry_run=dry)


if __name__ == "__main__":
    main_cli()
