#!/usr/bin/env python3
"""
Diagnóstico de entorno (doctor): dependencias Python, binarios opcionales, red opcional.

No importa pygame ni edge_tts al cargar el módulo; las pruebas son bajo demanda.
"""

from __future__ import annotations

import importlib
import os
import shutil
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class DoctorCheck:
    """Una fila del informe doctor."""

    name: str
    ok: bool
    critical: bool
    detail: str


def _truthy_skip_network() -> bool:
    return os.getenv("JARVIS_DOCTOR_SKIP_NETWORK", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _truthy_text_only() -> bool:
    return os.getenv("JARVIS_TEXT_ONLY", "").strip().lower() in ("1", "true", "yes", "on")


def _try_import(module: str) -> tuple[bool, str]:
    try:
        importlib.import_module(module)
        return True, "import ok"
    except Exception as e:
        return False, str(e)


def _which(name: str) -> tuple[bool, str]:
    p = shutil.which(name)
    if p:
        return True, p
    return False, "no en PATH"


def _tcp_cloudflare() -> tuple[bool, str]:
    if _truthy_skip_network():
        return True, "omitido (JARVIS_DOCTOR_SKIP_NETWORK)"
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=3)
        return True, "1.1.1.1:443 alcanzable"
    except OSError as e:
        return False, str(e)


def collect_doctor_report(
    *,
    music_file: str | None = None,
    which_fn: Callable[[str], str | None] | None = None,
) -> list[DoctorCheck]:
    """
    Genera la lista de comprobaciones. `music_file` ruta expandida del MPJ (opcional).
    `which_fn` permite inyectar shutil.which en tests.
    """
    w = which_fn or shutil.which
    checks: list[DoctorCheck] = []

    py_ok = sys.version_info >= (3, 9)
    checks.append(
        DoctorCheck(
            name="python",
            ok=py_ok,
            critical=True,
            detail=f"{sys.version.split()[0]} (>= 3.9 requerido)" if py_ok else f"{sys.version} — se requiere Python 3.9+",
        )
    )

    for mod, label in (
        ("edge_tts", "edge-tts"),
        ("psutil", "psutil"),
        ("requests", "requests"),
    ):
        ok, msg = _try_import(mod)
        checks.append(
            DoctorCheck(
                name=f"pip:{label}",
                ok=ok,
                critical=True,
                detail=msg,
            )
        )

    if _truthy_text_only():
        checks.append(
            DoctorCheck(
                name="pygame",
                ok=True,
                critical=False,
                detail="omitido (JARVIS_TEXT_ONLY=1)",
            )
        )
    else:
        ok, msg = _try_import("pygame")
        checks.append(
            DoctorCheck(
                name="pip:pygame",
                ok=ok,
                critical=True,
                detail=msg,
            )
        )

    for exe, label, critical in (
        ("cursor", "Cursor IDE", False),
        ("opencode", "OpenCode", False),
        ("wmctrl", "wmctrl (X11)", False),
        ("notify-send", "libnotify", False),
        ("xdg-open", "xdg-utils", False),
        ("nmcli", "NetworkManager CLI", False),
        ("xset", "xset (X11)", False),
        ("grim", "grim (captura Wayland)", False),
        ("scrot", "scrot (captura X11)", False),
        ("pactl", "PulseAudio/PipeWire pactl", False),
        ("beep", "beep (pcspkr)", False),
    ):
        path = w(exe)
        ok = path is not None
        checks.append(
            DoctorCheck(
                name=f"bin:{exe}",
                ok=ok,
                critical=critical,
                detail=path or "no instalado",
            )
        )

    mf = music_file or ""
    if mf:
        p = Path(mf).expanduser()
        exists = p.is_file()
        checks.append(
            DoctorCheck(
                name="música MP3",
                ok=exists,
                critical=False,
                detail=str(p) if exists else f"no encontrado: {p}",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="música MP3",
                ok=True,
                critical=False,
                detail="(no se pasó ruta; use JARVIS_MUSIC_FILE)",
            )
        )

    net_ok, net_msg = _tcp_cloudflare()
    checks.append(
        DoctorCheck(
            name="red (1.1.1.1:443)",
            ok=net_ok,
            critical=False,
            detail=net_msg,
        )
    )

    disp = bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))
    checks.append(
        DoctorCheck(
            name="sesión gráfica",
            ok=disp,
            critical=False,
            detail="DISPLAY/WAYLAND definido" if disp else "sin DISPLAY/WAYLAND (modo consola/SSH)",
        )
    )

    return checks


def doctor_exit_code(checks: list[DoctorCheck]) -> int:
    """0 si todas las comprobaciones críticas pasan."""
    for c in checks:
        if c.critical and not c.ok:
            return 1
    return 0


def format_doctor_report(checks: list[DoctorCheck]) -> str:
    lines = ["Jarvis doctor — informe", "=" * 40]
    for c in checks:
        mark = "OK " if c.ok else "FALLO "
        crit = "[crítico] " if c.critical else "[opcional] "
        lines.append(f"  {mark}{crit}{c.name}: {c.detail}")
    lines.append("=" * 40)
    lines.append("Código de salida 0 = requisitos críticos cumplidos.")
    return "\n".join(lines)


def run_doctor_cli(*, music_file: str | None = None) -> int:
    checks = collect_doctor_report(music_file=music_file)
    print(format_doctor_report(checks))
    return doctor_exit_code(checks)
