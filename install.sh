#!/usr/bin/env bash
# Instala dependencias en un venv junto al repo (idea lista: onboarding reproducible).
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
./venv/bin/pip install -U pip
./venv/bin/pip install -r requirements.txt
echo "Listo. Activa con: source venv/bin/activate"
echo "Prueba: ./jarvis --dry-run"
