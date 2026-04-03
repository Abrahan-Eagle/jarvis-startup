# Jarvis — bienvenida al iniciar (Linux)

**jarvis-startup** — arranque de sesión (voz, música opcional, taller).

Asistente local inspirado en la **idea** del Jarvis de *Iron Man*: voz que te trata con respeto (“señor”), informe de “sistemas”, música épica opcional y apertura del taller (OpenCode + Cursor). **No es oficial** de Marvel/Disney; es un homenaje para tu flujo de trabajo.

## Qué hace

1. Saluda por voz (Edge TTS) con tono configurable: **`iron`** (estilo mayordomo IA) o **`minimal`** (frases cortas).
2. Opcional: clima (`wttr.in`) y uso de CPU/RAM (reintento si falla la red).
3. Reproduce un MP3 de fondo en bucle durante la secuencia (por defecto `~/jarvis-startup/iron_music.mp3`; configurable con `JARVIS_MUSIC_FILE`).
4. Abre OpenCode y Cursor; opcionalmente mosaico con `wmctrl` (X11).
5. Notificación de escritorio (`notify-send`) al terminar, si está instalado.
6. Detiene la música al finalizar con **fade-out** opcional (configurable).
7. Opcional: segundo chime al abrir el IDE (`JARVIS_IDE_CHIME`), modo **privacidad** para videollamadas, aviso en **Wayland** si usas `wmctrl`, y **espeak** si Edge TTS falla.
8. Opcional: **HUD** en una ventana pequeña (hora, host, CPU/RAM) tras la secuencia (`JARVIS_HUD=1`, requiere `python3-tk`).

## Inspiración Iron Man (ideas de tono, no copia)

| Idea | En este proyecto |
|------|-------------------|
| IA que habla con cortesía al inventor | `JARVIS_THEME=iron`, `JARVIS_TITULO` = cómo te llama la voz |
| “Taller” / casa | Frases como “Bienvenido al taller” / “Bienvenido a casa” según la hora |
| Informes de sistemas | CPU, RAM, clima en la segunda frase |
| Música épica de fondo | MP3 vía `JARVIS_MUSIC_FILE` o por defecto `~/jarvis-startup/iron_music.mp3` |
| Sonido tipo HUD al arrancar | Opcional: `JARVIS_BOOT_SOUND` apunta a un `.wav` / `.ogg` corto (reproducido una vez al inicio) |
| Voz en otro idioma | `JARVIS_TTS_VOICE` (ej. inglés: `en-US-GuyNeural`) |
| Capa visual “taller” | Overlay opcional [`hud_overlay.py`](hud_overlay.py) con `JARVIS_HUD=1` |

## Requisitos

- Linux (GNOME + `kgx` si lo tienes).
- Python 3.9+

```bash
pip install -r requirements.txt
```

Opcionales: `wmctrl`, `notify-send` (paquete `libnotify`), `xrandr`, `espeak-ng` o `espeak` (respaldo de voz sin red), `python3-tk` (HUD).

## Uso rápido

```bash
./jarvis
# Simular sin voz, música ni abrir apps (útil para pruebas)
./jarvis --dry-run
# Subcomandos (equivalente a invocar sin subcomando = `run`)
./jarvis run --dry-run
./jarvis doctor          # comprueba Python, pip, binarios opcionales, red (opcional)
./jarvis version
# Forma explícita
python bienvenido_jarvis.py
python bienvenido_jarvis.py --version
```

En CI o sin red, `JARVIS_DOCTOR_SKIP_NETWORK=1 ./jarvis doctor` evita comprobar TCP a 1.1.1.1.

## Configuración en archivo (opcional)

Precedencia: **variables de entorno** > **`~/.config/jarvis-startup/config.json`** > perfil en código (`default` / `taller` / `casa`).

Claves admitidas en JSON: `titulo`, `project`, `theme`, `music_file`, `profile`. Ejemplo:

```json
{
  "profile": "casa",
  "titulo": "señor",
  "project": "~/Documentos/mi_repo"
}
```

Con `JARVIS_CONFIG_STRICT=1`, claves desconocidas en el JSON generan aviso en stderr.

Roadmap priorizado estilo película: [`docs/ROADMAP_PELICULA.md`](docs/ROADMAP_PELICULA.md).

### Inicio de sesión (autostart)

La secuencia principal **no es un demonio**: al terminar voz, música y apertura de apps, el proceso **sale**. Puede seguir abierta la ventana del **HUD** (`JARVIS_HUD=1`) o Cursor/OpenCode, pero **no** queda un proceso `jarvis` escuchando en segundo plano.

Para lanzarlo **al entrar en el escritorio**:

1. **Recomendado:** ejecuta una vez [`scripts/install_xdg_autostart.sh`](scripts/install_xdg_autostart.sh) — genera `~/.config/autostart/jarvis-bienvenida.desktop` con **rutas absolutas** (evita el fallo típico de dejar `TU_USUARIO` en el ejemplo). Por defecto **retraso 0 s** al iniciar sesión (lanza en cuanto el escritorio ejecuta el autostart); si ya tenías un `.desktop` antiguo con 15 s, **vuelve a ejecutar el instalador** para actualizarlo.
2. Manual: copia [`contrib/jarvis.desktop.example`](contrib/jarvis.desktop.example) a `~/.config/autostart/`, sustituye **todas** las rutas por las tuyas y `chmod +x jarvis scripts/jarvis_autostart.sh`.
3. [`scripts/jarvis_autostart.sh`](scripts/jarvis_autostart.sh): retraso `JARVIS_AUTOSTART_DELAY_SEC`, log en `~/.local/share/jarvis-startup/autostart.log` (`JARVIS_AUTOSTART_LOG=0` para desactivar).
4. Alternativa **systemd --user**: [`contrib/jarvis-user.service.example`](contrib/jarvis-user.service.example).

Si **no arranca tras reiniciar**, sigue [docs/TROUBLESHOOTING_AUTOSTART.md](docs/TROUBLESHOOTING_AUTOSTART.md).

Más detalle: [`docs/CONTRIB.md`](docs/CONTRIB.md).

## Variables de entorno

Tabla canónica: **[docs/ENV.md](docs/ENV.md)** (incluye HUD, lista extendida, segundo proyecto Cursor, requisitos de red/monitor, icono de notificación, etc.).

## Versión

Actual **2.3.4** en `bienvenido_jarvis.py` (`__version__`); ver con `jarvis version` o `--version`. Cobertura de la lista 1–100: [docs/COBERTURA_IDEAS.md](docs/COBERTURA_IDEAS.md).
