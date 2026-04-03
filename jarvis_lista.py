#!/usr/bin/env python3
"""
Cobertura de ideas 1–100 de docs/LISTA_IDEAS_COHERENTES_PELICULA.md.

- Con JARVIS_LISTA_COMPLETA=1 se añaden anexos de diagnóstico y matices de voz
  (respetando JARVIS_PRIVACY_MODE: no añade datos extra).
- Variables documentadas en docs/ENV.md y scripts en contrib/ (systemd, install, CI, tests).

Este módulo NO importa pygame ni edge_tts para poder usarse en pruebas ligeras.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Directorio de datos de aplicación (alineado con el nombre del repo: jarvis-startup)
XDG_APP_DIR = "jarvis-startup"

# ── Idea 70: niveles Mark (1–7) afectan volumen musical sugerido (el caller aplica) ──


def mark_level() -> int:
    try:
        v = int(os.getenv("JARVIS_MARK_LEVEL", "4").strip())
        return max(1, min(7, v))
    except ValueError:
        return 4


def mark_music_volume_factor() -> float:
    """Factor 0.35–1.0 según Mark."""
    return 0.25 + (mark_level() / 7.0) * 0.75


# ── Voz / personalidad (1–15) ──

_SALUDOS_VARIANTES = [
    "¿En qué trabajamos hoy?",
    "¿Qué prioridad tiene el taller?",
    "Sistemas listos para su instrucción.",
]

_CITAS_ING = [
    "Integridad estructural dentro de parámetros.",
    "Límites térmicos y eléctricos en rango nominal.",
    "Calibración de sensores estable.",
]

_WITTY = [
    "El café sigue siendo responsabilidad humana.",
    "Sin ironía en los núcleos: todo en verde.",
]


def voice_mode() -> str:
    return os.getenv("JARVIS_VOICE_MODE", "mayordomo").strip().lower()


def enhance_lines(
    line1: str,
    line2: str,
    *,
    privacy: bool,
    lista_completa: bool,
    titulo: str,
    theme: str,
) -> tuple[str, str]:
    """Ideas 1–5, 9–11, 15: variantes, modo voz, subtítulos ya van por consola; aquí ajustamos texto."""
    if privacy:
        return line1, line2

    l1, l2 = line1, line2

    if os.getenv("JARVIS_RANDOM_OPENING", "").strip().lower() in ("1", "true", "yes", "on"):
        if theme == "iron" and "¿En qué trabajamos" in l1:
            l1 = l1.replace("¿En qué trabajamos hoy?", random.choice(_SALUDOS_VARIANTES))

    code = os.getenv("JARVIS_CODE_NAME", "").strip()
    if code and lista_completa:
        l1 = f"{l1} Proyecto en clave «{code}»."

    vm = voice_mode()
    if lista_completa and vm == "militar":
        l2 = l2.replace("Diagnóstico:", "Informe breve:")
        l2 = l2.replace("Todo dentro de parámetros", "Parámetros dentro de norma")

    if os.getenv("JARVIS_WITTY", "").strip().lower() in ("1", "true", "yes", "on") and lista_completa:
        l2 = f"{l2} {random.choice(_WITTY)}"

    if os.getenv("JARVIS_ENGINEER_QUOTE", "").strip().lower() in ("1", "true", "yes", "on") and lista_completa:
        l2 = f"{l2} {random.choice(_CITAS_ING)}"

    briefing = os.path.expanduser(os.getenv("JARVIS_BRIEFING_FILE", "").strip())
    if briefing and os.path.isfile(briefing) and lista_completa:
        try:
            with open(briefing, encoding="utf-8", errors="replace") as f:
                first = f.readline().strip()
            if first:
                l2 = f"{l2} Briefing: {first[:200]}"
        except OSError:
            pass

    return l1, l2


def _run(cmd: list[str], timeout: float = 2.5) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _sn_temp() -> str:
    try:
        p = Path("/sys/class/thermal/thermal_zone0/temp")
        if p.is_file():
            raw = int(p.read_text().strip())
            t = raw / 1000.0
            if t > 80 and os.getenv("JARVIS_THERMAL_WARN", "1").lower() not in ("0", "false"):
                return f"Sobrecarga térmica simulada: {t:.0f} grados en zona crítica."
            return f"Temperatura aproximada del núcleo {t:.0f} grados."
    except (OSError, ValueError):
        pass
    return ""


def _sn_net() -> str:
    try:
        import psutil

        io = psutil.net_io_counters()
        return f"Tráfico acumulado: enviados {io.bytes_sent // 1_048_576} MiB, recibidos {io.bytes_recv // 1_048_576} MiB."
    except Exception:
        return ""


def _sn_ping_gateway() -> str:
    if os.getenv("JARVIS_SKIP_PING", "").lower() in ("1", "true", "yes"):
        return ""
    try:
        r = _run(["ip", "route", "show", "default"], 1.5)
        m = re.search(r"via (\d+\.\d+\.\d+\.\d+)", r.stdout or "")
        if not m:
            return ""
        gw = m.group(1)
        p = _run(["ping", "-c", "1", "-W", "1", gw], 3)
        ok = p.returncode == 0
        return f"Enlace al gateway: {'estable' if ok else 'inestable'}."
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _sn_top3() -> str:
    try:
        import psutil

        procs = sorted(
            (p for p in psutil.process_iter(["name", "cpu_percent"])),
            key=lambda x: (x.info.get("cpu_percent") or 0),
            reverse=True,
        )[:3]
        names = [p.info.get("name") or "?" for p in procs]
        return f"Procesos con más actividad: {', '.join(names)}."
    except Exception:
        return ""


def _sn_boot() -> str:
    try:
        import psutil

        t = datetime.fromtimestamp(psutil.boot_time())
        return f"Último arranque del sistema: {t.strftime('%Y-%m-%d %H:%M')}."
    except Exception:
        return ""


def _sn_journal_err() -> str:
    try:
        r = _run(
            ["journalctl", "-p", "err", "-n", "1", "--no-pager", "-q"],
            2.5,
        )
        line = (r.stdout or "").strip().splitlines()
        if line and len(line[0]) < 180:
            return f"Último error del registro: {line[0][:160]}."
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _sn_docker() -> str:
    if not shutil.which("docker"):
        return ""
    r = _run(["docker", "ps", "-q"], 2.0)
    if r.returncode != 0:
        return ""
    n = len([x for x in (r.stdout or "").splitlines() if x.strip()])
    return f"Contenedores activos: {n}."


def _sn_libvirt() -> str:
    if not shutil.which("virsh"):
        return ""
    r = _run(["virsh", "list", "--name"], 2.0)
    if r.returncode != 0:
        return ""
    names = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    return f"Máquinas virtuales definidas: {len(names)}."


def _sn_tmp() -> str:
    try:
        u = shutil.disk_usage("/tmp")
        pct = int(100 * (u.used / u.total)) if u.total else 0
        return f"/tmp al {pct} por ciento de uso."
    except OSError:
        return ""


def _sn_inodes_home() -> str:
    try:
        r = _run(["df", "-i", os.path.expanduser("~")], 2.0)
        if r.returncode == 0 and (r.stdout or "").strip():
            parts = (r.stdout or "").strip().splitlines()[-1].split()
            if len(parts) >= 5:
                return f"Inodos libres en $HOME aproximadamente {parts[3]}."
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _sn_vpn() -> str:
    p = Path("/sys/class/net")
    try:
        for name in p.iterdir():
            if name.name.startswith(("tun", "wg", "ppp")):
                return f"Interfaz tipo túnel activa: {name.name}."
    except OSError:
        pass
    return ""


def _sn_env_perms(root: str) -> str:
    envp = Path(root) / ".env"
    try:
        if envp.is_file():
            mode = oct(envp.stat().st_mode)[-3:]
            if mode > "644":
                return f"Atención: .env con permisos {mode}; considere chmod 600."
    except OSError:
        pass
    return ""


def _sn_git_ahead(root: str) -> str:
    git = Path(root) / ".git"
    if not git.is_dir():
        return ""
    try:
        upstream = _run(["git", "-C", root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], 2)
        if upstream.returncode != 0:
            return ""
        lr = _run(["git", "-C", root, "rev-list", "--left-right", "--count", "HEAD...@{u}"], 2)
        if lr.returncode != 0:
            return ""
        parts = (lr.stdout or "").strip().split()
        if len(parts) == 2:
            left, right = parts[0], parts[1]
            return f"Sincronización con remoto: {left} locales / {right} remotos."
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def _sn_branch_warn(root: str) -> str:
    git = Path(root) / ".git"
    if not git.is_dir():
        return ""
    r = _run(["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"], 1.5)
    if r.returncode != 0:
        return ""
    b = (r.stdout or "").strip()
    if b not in ("main", "master", "dev", "develop"):
        return f"Rama actual «{b}»; verifique antes de integrar."
    return ""


def _sn_makefile(root: str) -> str:
    for name in ("Makefile", "justfile"):
        if (Path(root) / name).is_file():
            return f"Se detectó {name} en el proyecto."
    return ""


def _sn_uptime_pause() -> str:
    try:
        import psutil

        h = (time.time() - psutil.boot_time()) / 3600.0
        lim = float(os.getenv("JARVIS_UPTIME_PAUSE_H", "10"))
        if h > lim:
            return f"Sesión larga: más de {lim:.0f} horas desde el arranque; conviene una pausa."
    except Exception:
        pass
    return ""


def _moon_phase() -> str:
    # Idea 68: aproximación muy simple
    synodic = 29.53059
    known = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days = (now - known).total_seconds() / 86400.0
    phase = (days % synodic) / synodic
    names = ["nueva", "creciente", "llena", "menguante"]
    idx = int(phase * 4) % 4
    return f"Luna hoy en fase aproximada {names[idx]}."


def _birthday_msg() -> str:
    bd = os.getenv("JARVIS_BIRTHDAY_MM_DD", "").strip()
    if not bd or len(bd) != 5:
        return ""
    today = datetime.now().strftime("%m-%d")
    if bd == today:
        return "Feliz cumpleaños, señor. Los sistemas celebran con usted."
    return ""


def _streak_update() -> str:
    path = Path.home() / ".local/share" / XDG_APP_DIR / "streak.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {}
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
        last = data.get("date")
        today = datetime.now().strftime("%Y-%m-%d")
        n = int(data.get("n", 0))
        if last == today:
            return f"Racha de taller: {n} día(s) consecutivos con Jarvis."
        if last:
            from datetime import timedelta

            y = datetime.strptime(last, "%Y-%m-%d") + timedelta(days=1)
            if y.strftime("%Y-%m-%d") == today:
                n += 1
            else:
                n = 1
        else:
            n = 1
        data = {"date": today, "n": n}
        path.write_text(json.dumps(data), encoding="utf-8")
        return f"Racha de taller: {n} día(s) consecutivos."
    except OSError:
        return ""


def _milestone_msg() -> str:
    # Idea 97: fechas históricas de ingeniería (muestra)
    hits = {
        "03-09": "Un día como hoy en la historia: nace la idea de conmutación programada.",
        "07-20": "Recuerde: el primer paso en la Luna fue un hito de sistemas y control.",
    }
    return hits.get(datetime.now().strftime("%m-%d"), "")


def _brightness_phrase() -> str:
    p = shutil.which("brightnessctl")
    if not p:
        return ""
    r = _run([p, "get"], 1.5)
    if r.returncode == 0 and (r.stdout or "").strip():
        return f"Brillo del visor: {(r.stdout or '').strip()}."
    return ""


def _hash_integrity() -> str:
    fp = os.getenv("JARVIS_INTEGRITY_FILE", "").strip()
    if not fp:
        return ""
    p = Path(os.path.expanduser(fp))
    if not p.is_file():
        return ""
    try:
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        return f"Huella simbólica del artefacto: {h}."
    except OSError:
        return ""


def _protocol_file() -> str:
    pf = os.path.expanduser(os.getenv("JARVIS_PROTOCOL_FILE", "").strip())
    if not pf or not Path(pf).is_file():
        return ""
    try:
        lines = Path(pf).read_text(encoding="utf-8", errors="replace").splitlines()
        items = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")][:5]
        if items:
            return "Protocolo de laboratorio: " + "; ".join(items[:3]) + "."
    except OSError:
        pass
    return ""


def _security_reminder() -> str:
    sf = os.path.expanduser(os.getenv("JARVIS_SECURITY_REMINDER_FILE", "").strip())
    if sf and Path(sf).is_file():
        try:
            t = Path(sf).read_text(encoding="utf-8", errors="replace").strip()[:200]
            if t:
                return f"Recordatorio de seguridad: {t}"
        except OSError:
            pass
    if os.getenv("JARVIS_DEFAULT_2FA_REMINDER", "").lower() in ("1", "true", "yes"):
        return "Recuerde revisar 2FA y rotación de claves según política del taller."
    return ""


def _sn_isolated_notice() -> str:
    """Idea 46: aviso texto, sin tocar firewall."""
    if os.getenv("JARVIS_ISOLATED_NOTICE", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    return (
        "Modo aislado: Jarvis no configura el cortafuegos; "
        "revise manualmente el tráfico saliente si opera en red restringida."
    )


def _sn_updates_pending() -> str:
    """Idea 42: resumen ligero de actualizaciones pendientes (timeout corto)."""
    if os.getenv("JARVIS_SKIP_UPDATES_CHECK", "").strip().lower() in ("1", "true", "yes", "on"):
        return ""
    if shutil.which("apt-get"):
        r = _run(
            ["bash", "-c", "apt-get -s upgrade 2>/dev/null | grep -c '^Inst ' || true"],
            12,
        )
        if r.returncode == 0 and (r.stdout or "").strip().isdigit():
            n = int((r.stdout or "").strip())
            if n > 0:
                return f"Paquetes con actualización simulada disponible: {n}."
    if shutil.which("dnf"):
        r = _run(["dnf", "check-update", "--quiet"], 15)
        if r.returncode == 100:
            lines = [x for x in (r.stdout or "").splitlines() if x.strip()]
            return f"Actualizaciones DNF pendientes: aproximadamente {len(lines)} entradas."
    if shutil.which("checkupdates"):
        r = _run(["checkupdates"], 20)
        if r.returncode == 0 and (r.stdout or "").strip():
            n = len([x for x in (r.stdout or "").splitlines() if x.strip()])
            return f"Actualizaciones pacman pendientes: {n}."
    return ""


def _sn_net_iface_active() -> str:
    """Idea 34: interfaces activas (sin contadores delta, evita CPU)."""
    try:
        import psutil

        stats = psutil.net_if_stats()
        up = [k for k, v in stats.items() if v.isup and not k.startswith("lo")]
        if up:
            return f"Interfaces en servicio: {', '.join(sorted(up)[:6])}."
    except Exception:
        pass
    return ""


def _sn_git_status_short(root: str) -> str:
    """Idea 53: primera línea de git status -sb."""
    if os.getenv("JARVIS_GIT_STATUS_ANNEX", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    if not (Path(root) / ".git").exists():
        return ""
    r = _run(["git", "-C", root, "status", "-sb"], 3)
    if r.returncode != 0:
        return ""
    line = (r.stdout or "").splitlines()[0].strip() if (r.stdout or "").strip() else ""
    if line:
        return f"Estado git: {line[:160]}."
    return ""


def _field_test_count_bump() -> int:
    """Idea 71: incrementa contador cuando JARVIS_TEST_CMD termina con éxito."""
    path = Path.home() / ".local/share" / XDG_APP_DIR / "field_tests.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        n = 0
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            n = int(data.get("n", 0))
        n += 1
        path.write_text(
            json.dumps({"n": n, "last_ok": datetime.now().isoformat()}),
            encoding="utf-8",
        )
        return n
    except (OSError, json.JSONDecodeError, ValueError):
        return 0


def _sn_test_cmd_exit() -> str:
    """Idea 57: comando de prueba configurable; solo código de salida."""
    cmd = os.getenv("JARVIS_TEST_CMD", "").strip()
    if not cmd:
        return ""
    try:
        to = float(os.getenv("JARVIS_TEST_CMD_TIMEOUT", "60"))
    except ValueError:
        to = 60.0
    to = max(5.0, min(120.0, to))
    r = _run(["bash", "-c", cmd], to)
    extra = ""
    if r.returncode == 0:
        n = _field_test_count_bump()
        if n > 0:
            extra = f" Pruebas de campo exitosas acumuladas: {n}."
    return f"Prueba configurada del taller: código de salida {r.returncode}.{extra}"


def _sn_tasks_file() -> str:
    """Ideas 6–7: tareas desde JSON o Markdown."""
    tf = os.getenv("JARVIS_TASKS_FILE", "").strip()
    if not tf:
        return ""
    p = Path(os.path.expanduser(tf))
    if not p.is_file():
        return ""
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
        if p.suffix.lower() == ".json":
            data = json.loads(raw)
            if isinstance(data, list) and data:
                first = data[0]
                if isinstance(first, dict) and first.get("title"):
                    return f"Tarea prioritaria: {str(first['title'])[:120]}."
                return f"Tareas cargadas: {len(data)} entrada(s)."
            if isinstance(data, dict) and "tasks" in data:
                t = data["tasks"]
                if isinstance(t, list) and t:
                    return f"Plan del día: {str(t[0])[:120]}."
        for ln in raw.splitlines():
            s = ln.strip()
            if s.startswith(("- ", "* ", "1.")):
                return f"Pendiente: {s.lstrip('-*0123456789. ')[:160]}"
    except (OSError, json.JSONDecodeError):
        pass
    return ""


def _sn_ics_reminder() -> str:
    """Ideas 66, 69: evento .ics próximo (simple) y recordatorio 15 min."""
    path = os.getenv("JARVIS_ICS_FILE", "").strip()
    if not path:
        return ""
    p = Path(os.path.expanduser(path))
    if not p.is_file():
        return ""
    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m_sum = re.search(r"SUMMARY:([^\r\n]+)", raw)
    m_dt = re.search(r"DTSTART(?:;[^:]*)?:([0-9TZ]+)", raw)
    summary = (m_sum.group(1).strip() if m_sum else "Evento").replace("\\,", ",")
    if not m_dt:
        return f"Calendario local: {summary[:80]}."
    ds = m_dt.group(1).strip()
    evt: datetime | None = None
    try:
        if "Z" in ds:
            evt = datetime.fromisoformat(ds.replace("Z", "+00:00"))
            if evt.tzinfo:
                evt = evt.astimezone().replace(tzinfo=None)
        elif len(ds) >= 15 and "T" in ds:
            evt = datetime.strptime(ds[:15], "%Y%m%dT%H%M%S")
        elif len(ds) == 8:
            evt = datetime.strptime(ds, "%Y%m%d")
    except ValueError:
        evt = None
    if evt:
        now = datetime.now()
        delta = (evt - now).total_seconds() / 60.0
        if 0 <= delta <= 15:
            return f"Reunión en los próximos quince minutos: {summary[:100]}."
        if delta > 15:
            return f"Próximo evento .ics: {summary[:80]} ({evt.strftime('%Y-%m-%d %H:%M')})."
    return f"Calendario local: {summary[:100]}."


def _sn_optional_pcspkr_beep() -> str:
    """Idea 23: beep opcional (beep o speaker-test), sin fallar si no hay hardware."""
    if os.getenv("JARVIS_PCSPKR_BEEP", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    if shutil.which("beep"):
        _run(["beep", "-f", "1000", "-l", "40"], 1.0)
        return "Beep de sistema opcional emitido (comando beep)."
    return "Beep opcional solicitado: instale el paquete «beep» (pcspkr) si desea tono en consola."


def _sn_xrandr_monitors() -> str:
    """Idea 86: número de salidas conectadas vía xrandr."""
    if not shutil.which("xrandr"):
        return ""
    r = _run(["bash", "-c", "xrandr 2>/dev/null | grep -c ' connected' || true"], 3)
    if r.returncode != 0:
        return ""
    raw = (r.stdout or "").strip()
    if not raw.isdigit():
        return ""
    n = int(raw)
    if n <= 0:
        return ""
    return f"Pantallas detectadas (xrandr): {n} salida(s) conectada(s)."


def _sn_pactl_audio() -> str:
    """Idea 88: sink por defecto (PipeWire/PulseAudio)."""
    if not shutil.which("pactl"):
        return ""
    r = _run(["pactl", "get-default-sink"], 2)
    if r.returncode != 0:
        return ""
    sink = (r.stdout or "").strip()
    if not sink:
        return ""
    return f"Audio: sink por defecto «{sink[:100]}»."


def _sn_focus_windows_hint() -> str:
    """Idea 64: minimizar todo salvo IDE — solo guía; ver contrib."""
    if os.getenv("JARVIS_FOCUS_WINDOWS_HINT", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    return (
        "Enfoque de ventanas: use reglas del compositor o "
        "«contrib/jarvis-window-hints.stub.sh»; Jarvis no minimiza ventanas ajenas."
    )


def _sn_gpg_release_hint() -> str:
    """Idea 51: firma GPG — guía en contrib."""
    if os.getenv("JARVIS_GPG_RELEASE_HINT", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    return "Release: firme artefactos con GPG según «contrib/gpg-sign-release.example.sh»."


def _sn_voice_chat_hint() -> str:
    """Idea 78: chat por voz con IA externa al proceso principal."""
    if os.getenv("JARVIS_VOICE_CHAT_HINT", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    return (
        "Chat voz: use un cliente compatible con Ollama o su API; "
        "ver «contrib/README-voice-chat-hint.md»."
    )


def _ollama_commit_suggestion(root: str) -> str:
    """Idea 77: sugerencia de mensaje de commit vía Ollama (opt-in)."""
    if os.getenv("JARVIS_OLLAMA_COMMIT_MSG", "").strip().lower() not in ("1", "true", "yes", "on"):
        return ""
    host = os.getenv("OLLAMA_HOST", "").strip()
    model = os.getenv("JARVIS_OLLAMA_MODEL", "").strip()
    if not host or not model:
        return ""
    git_dir = Path(root) / ".git"
    if not git_dir.exists():
        return ""
    stat = _run(["git", "-C", root, "diff", "--stat"], 4)
    diff_preview = (stat.stdout or "").strip()[:1200]
    if not diff_preview:
        return ""
    try:
        import urllib.request

        prompt = (
            "Responde UNA sola línea: mensaje de commit convencional en español "
            "(tipo prefijo: ámbito) para estos cambios:\n"
            f"{diff_preview}"
        )
        req = urllib.request.Request(
            f"{host.rstrip('/')}/api/generate",
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode())
        t = (body.get("response") or "").strip().splitlines()[0][:240]
        return f"Sugerencia de commit (IA local): {t}" if t else ""
    except Exception:
        return ""


def _ollama_line() -> str:
    host = os.getenv("OLLAMA_HOST", "").strip()
    model = os.getenv("JARVIS_OLLAMA_MODEL", "").strip()
    if not host or not model:
        return ""
    try:
        import urllib.request

        req = urllib.request.Request(
            f"{host.rstrip('/')}/api/generate",
            data=json.dumps(
                {
                    "model": model,
                    "prompt": "Di una sola frase breve estilo IA de laboratorio en español.",
                    "stream": False,
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = json.loads(resp.read().decode())
        t = (body.get("response") or "").strip().splitlines()[0][:220]
        return f"IA local: {t}" if t else ""
    except Exception:
        return ""


def build_saludo_annex(
    *,
    privacy: bool,
    lista_completa: bool,
    new_project: str,
) -> str:
    """Texto adicional para la segunda frase (ideas 32–45, 47–50, 54–57, 65–69, 76, 85–88, 95–97)."""
    if privacy or not lista_completa:
        return ""

    parts: list[str] = []
    root = os.path.expanduser(new_project)

    for fn in (
        _sn_isolated_notice,
        _sn_gpg_release_hint,
        _sn_voice_chat_hint,
        _sn_focus_windows_hint,
        _sn_optional_pcspkr_beep,
        _sn_xrandr_monitors,
        _sn_pactl_audio,
        _sn_tasks_file,
        _sn_ics_reminder,
        _sn_temp,
        _sn_net,
        _sn_net_iface_active,
        _sn_ping_gateway,
        _sn_top3,
        _sn_boot,
        _sn_journal_err,
        _sn_docker,
        _sn_libvirt,
        _sn_tmp,
        _sn_inodes_home,
        _sn_vpn,
        lambda: _sn_env_perms(root),
        lambda: _sn_git_ahead(root),
        lambda: _sn_branch_warn(root),
        lambda: _sn_git_status_short(root),
        lambda: _sn_makefile(root),
        _sn_updates_pending,
        _sn_test_cmd_exit,
        _sn_uptime_pause,
        _moon_phase,
        _birthday_msg,
        _streak_update,
        _milestone_msg,
        _brightness_phrase,
        _hash_integrity,
        _protocol_file,
        _security_reminder,
        _ollama_line,
        lambda: _ollama_commit_suggestion(root),
    ):
        try:
            s = fn()
            if s:
                parts.append(s)
        except Exception:
            continue

    raw = " ".join(parts)
    maxc = int(os.getenv("JARVIS_MAX_ANEXO_CHARS", "1400"))
    if len(raw) > maxc:
        raw = raw[: maxc - 3] + "..."
    return raw


def run_hooks(dry_run: bool) -> None:
    """Idea 92: ejecuta scripts en ~/.config/jarvis-startup/hooks.d/"""
    if dry_run:
        return
    d = Path.home() / ".config" / XDG_APP_DIR / "hooks.d"
    if not d.is_dir():
        return
    for script in sorted(d.glob("*.sh")):
        try:
            subprocess.run(["/bin/bash", str(script)], check=False, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            pass


def write_session_report(extra: dict[str, Any]) -> None:
    """Ideas 83–85: informe TXT + JSON enriquecido."""
    base = Path.home() / ".local/share" / XDG_APP_DIR
    try:
        base.mkdir(parents=True, exist_ok=True)
        p = base / "session_report.txt"
        line = f"{datetime.now().isoformat()} {json.dumps(extra, ensure_ascii=False)}\n"
        with open(p, "a", encoding="utf-8") as f:
            f.write(line)
        # rotación simple (84)
        lr = base / "last_run.json"
        if lr.is_file() and lr.stat().st_size > 512_000:
            lr.rename(base / "last_run.json.bak")
    except OSError:
        pass


def maybe_jitter_startup() -> None:
    """Idea 80."""
    if os.getenv("JARVIS_AUTOSTART_JITTER", "").lower() not in ("1", "true", "yes"):
        return
    time.sleep(random.uniform(0.0, 2.0))


def network_ok() -> bool:
    """Idea 81: conectividad (socket); opcionalmente nmcli si el socket falla."""
    if os.getenv("JARVIS_REQUIRE_NETWORK", "").lower() not in ("1", "true", "yes"):
        return True
    try:
        import socket

        socket.create_connection(("1.1.1.1", 443), timeout=3)
        return True
    except OSError:
        pass
    if os.getenv("JARVIS_NETWORK_NMCLI_FALLBACK", "1").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        return False
    nm = shutil.which("nmcli")
    if not nm:
        return False
    r = _run([nm, "-t", "-f", "STATE", "g"], 3)
    if r.returncode != 0:
        return False
    st = (r.stdout or "").strip().lower()
    return "connected" in st


def monitor_likely_on() -> bool:
    """Idea 82: DISPLAY/Wayland; opcionalmente xset q si JARVIS_MONITOR_XSET=1."""
    if os.getenv("JARVIS_REQUIRE_MONITOR", "").lower() not in ("1", "true", "yes"):
        return True
    if not (os.getenv("WAYLAND_DISPLAY") or os.getenv("DISPLAY")):
        return False
    if os.getenv("JARVIS_MONITOR_XSET", "").strip().lower() not in ("1", "true", "yes", "on"):
        return True
    disp = os.getenv("DISPLAY", "").strip()
    if not disp or not shutil.which("xset"):
        return True
    r = _run(["xset", "q"], 2.5)
    return r.returncode == 0
