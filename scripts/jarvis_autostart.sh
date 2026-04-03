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

_log() {
  if [[ "$DO_LOG" =~ ^(1|true|yes|on)$ ]]; then
    mkdir -p "$LOG_DIR"
    echo "$1" >>"$LOG_FILE"
  fi
}

if ! [[ "$DELAY" =~ ^[0-9]+$ ]]; then
  DELAY=0
fi
if (( DELAY > 0 )); then
  sleep "$DELAY"
fi

if [[ ! -f "$JARVIS" ]]; then
  _log "ERROR: no existe $JARVIS (¿ruta del repo correcta en el .desktop?)"
  exit 1
fi
if [[ ! -x "$JARVIS" ]]; then
  _log "ERROR: $JARVIS no es ejecutable. Ejecuta: chmod +x \"$JARVIS\""
  exit 1
fi

if [[ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  _log "AVISO: sin DISPLAY/WAYLAND; la bienvenida puede fallar o salir si exiges monitor gráfico."
fi

if [[ "$DO_LOG" =~ ^(1|true|yes|on)$ ]]; then
  mkdir -p "$LOG_DIR"
  {
    echo "===== $(date -Iseconds) inicio ====="
    echo "exec: $JARVIS pwd=$ROOT HOME=${HOME:-}"
    echo "DISPLAY=${DISPLAY:-} WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-}"
    "$JARVIS"
    ec=$?
    echo "===== fin código=$ec ====="
    exit "$ec"
  } >>"$LOG_FILE" 2>&1
else
  exec "$JARVIS"
fi
