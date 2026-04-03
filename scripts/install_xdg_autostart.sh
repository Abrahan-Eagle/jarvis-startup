#!/usr/bin/env bash
# Genera ~/.config/autostart/jarvis-bienvenida.desktop con rutas ABSOLUTAS al repo actual.
# Uso: /ruta/a/jarvis-startup/scripts/install_xdg_autostart.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
DESKTOP_FILE="$DESKTOP_DIR/jarvis-bienvenida.desktop"
# Default 0: arranque en cuanto el escritorio lance el autostart. Si DISPLAY/red tardan, usa p.ej. JARVIS_AUTOSTART_INSTALL_DELAY=15
DELAY="${JARVIS_AUTOSTART_INSTALL_DELAY:-0}"

mkdir -p "$DESKTOP_DIR"
chmod +x "$ROOT/jarvis" "$ROOT/scripts/jarvis_autostart.sh" 2>/dev/null || true

cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Jarvis Bienvenida
Comment=Bienvenida por voz y taller (jarvis-startup)
Exec=env JARVIS_AUTOSTART_DELAY_SEC=${DELAY} JARVIS_AUTOSTART_LOG=1 /bin/bash ${ROOT}/scripts/jarvis_autostart.sh
Path=${ROOT}
Icon=utilities-terminal
Terminal=false
Categories=Utility;
StartupNotify=false
DBusActivatable=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=${DELAY}
EOF

echo "Instalado: $DESKTOP_FILE"
echo "Log (tras la 1ª ejecución): cat ~/.local/share/jarvis-startup/autostart.log"
echo "Prueba: ./scripts/jarvis_autostart.sh   o   gio launch $DESKTOP_FILE"
echo "  (gtk-launch: sudo apt install libgtk-3-bin)"
