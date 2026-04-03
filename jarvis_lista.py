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
    path = Path.home() / ".local/share/jarvis/streak.json"
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
        _sn_temp,
        _sn_net,
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
        lambda: _sn_makefile(root),
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
    """Idea 92: ejecuta scripts en ~/.config/jarvis/hooks.d/"""
    if dry_run:
        return
    d = Path.home() / ".config/jarvis/hooks.d"
    if not d.is_dir():
        return
    for script in sorted(d.glob("*.sh")):
        try:
            subprocess.run(["/bin/bash", str(script)], check=False, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            pass


def write_session_report(extra: dict[str, Any]) -> None:
    """Ideas 83–85: informe TXT + JSON enriquecido."""
    base = Path.home() / ".local/share/jarvis"
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
    """Idea 81: comprobar conectividad básica."""
    if os.getenv("JARVIS_REQUIRE_NETWORK", "").lower() not in ("1", "true", "yes"):
        return True
    try:
        import socket

        socket.create_connection(("1.1.1.1", 443), timeout=3)
        return True
    except OSError:
        return False


def monitor_likely_on() -> bool:
    """Idea 82: heurística débil."""
    if os.getenv("JARVIS_REQUIRE_MONITOR", "").lower() not in ("1", "true", "yes"):
        return True
    if os.getenv("WAYLAND_DISPLAY") or os.getenv("DISPLAY"):
        return True
    return False
