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
# o
python bienvenido_jarvis.py
python bienvenido_jarvis.py --version
```

Roadmap priorizado estilo película: [`docs/ROADMAP_PELICULA.md`](docs/ROADMAP_PELICULA.md).

Autostart (ejemplo): copia y edita la ruta en [`contrib/jarvis.desktop.example`](contrib/jarvis.desktop.example) hacia `~/.config/autostart/`. Más opciones (venv, systemd, tests): [`docs/CONTRIB.md`](docs/CONTRIB.md).

## Variables de entorno

Tabla canónica: **[docs/ENV.md](docs/ENV.md)** (incluye HUD, lista extendida, segundo proyecto Cursor, requisitos de red/monitor, icono de notificación, etc.).

## Versión

Actual **2.1.0** en `bienvenido_jarvis.py` (`__version__`); ver con `--version`. Cobertura de la lista 1–100: [docs/COBERTURA_IDEAS.md](docs/COBERTURA_IDEAS.md).
