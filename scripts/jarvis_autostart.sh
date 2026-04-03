#!/usr/bin/env bash
# Arranque al iniciar sesión gráfica (XDG autostart o systemd --user).
# El script termina cuando termina ./jarvis: no deja un demonio en segundo plano.
# Opcional: JARVIS_AUTOSTART_DELAY_SEC (entero, segundos de espera antes de lanzar).
# Log: ~/.local/share/jarvis-startup/autostart.log si JARVIS_AUTOSTART_LOG=1 (default).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JARVIS="${ROOT}/jarvis"
LOG_DIR="${HOME}/.local/share/jarvis-startup"
LOG_FILE="${LOG_DIR}/autostart.log"
DELAY="${JARVIS_AUTOSTART_DELAY_SEC:-0}"
DO_LOG="${JARVIS_AUTOSTART_LOG:-1}"

if ! [[ "$DELAY" =~ ^[0-9]+$ ]]; then
  DELAY=0
fi
if (( DELAY > 0 )); then
  sleep "$DELAY"
fi

if [[ "$DO_LOG" =~ ^(1|true|yes|on)$ ]]; then
  mkdir -p "$LOG_DIR"
  {
    echo "===== $(date -Iseconds) inicio ====="
    echo "exec: $JARVIS"
    "$JARVIS"
    ec=$?
    echo "===== fin código=$ec ====="
    exit "$ec"
  } >>"$LOG_FILE" 2>&1
else
  exec "$JARVIS"
fi
