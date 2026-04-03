#!/usr/bin/env python3
"""
Carga opcional de ~/.config/jarvis-startup/config.json (sin dependencias extra).

Precedencia documentada: variables de entorno > config.json > perfil en código (PROFILES).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

CONFIG_DIR_NAME = "jarvis-startup"
KNOWN_KEYS = frozenset({"titulo", "project", "theme", "music_file", "profile"})


def config_path() -> Path:
    return Path.home() / ".config" / CONFIG_DIR_NAME / "config.json"


def load_user_config() -> dict[str, Any]:
    p = config_path()
    if not p.is_file():
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        if _strict():
            print(f"Jarvis: no se pudo leer {p}: {e}", file=sys.stderr)
        return {}
    if not isinstance(raw, dict):
        if _strict():
            print(f"Jarvis: {p} debe ser un objeto JSON.", file=sys.stderr)
        return {}
    for k in raw:
        if k not in KNOWN_KEYS and _strict():
            print(f"Jarvis: clave desconocida en config.json (omítala o use solo {sorted(KNOWN_KEYS)}): {k}", file=sys.stderr)
    return {k: raw[k] for k in raw if k in KNOWN_KEYS}


def _strict() -> bool:
    return os.getenv("JARVIS_CONFIG_STRICT", "").strip().lower() in ("1", "true", "yes", "on")
