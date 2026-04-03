#!/usr/bin/env python3
"""
Idea 14 (lista película): confirmación antes de acciones destructivas.

Uso en shell:
  ./scripts/jarvis_confirm.py "¿Borrar la carpeta?" && rm -rf ...

Con voz local (opcional):
  ./scripts/jarvis_confirm.py --speak "¿Confirmar?"
"""
from __future__ import annotations

import argparse
import shutil
import sys


def main() -> None:
    p = argparse.ArgumentParser(description="Confirmación sí/no (exit 0 = sí).")
    p.add_argument(
        "message",
        nargs="?",
        default="¿Confirmar esta acción destructiva?",
    )
    p.add_argument(
        "--speak",
        action="store_true",
        help="Intentar leer el mensaje con espeak-ng o espeak si existe.",
    )
    args = p.parse_args()

    if args.speak:
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        if exe:
            import subprocess

            subprocess.run([exe, args.message], check=False, capture_output=True)

    print(args.message, end=" [s/N] ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        raise SystemExit(1)
    if line.strip().lower() not in ("s", "si", "sí", "y", "yes"):
        raise SystemExit(1)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
