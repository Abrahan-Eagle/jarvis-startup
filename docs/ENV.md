# Variables de entorno (Jarvis)

Referencia única para `bienvenido_jarvis.py`, `jarvis_lista.py` y [`hud_overlay.py`](../hud_overlay.py). Valores tipo “verdadero”: `1`, `true`, `yes`, `on` (según variable).

| Variable | Descripción |
|----------|-------------|
| *(archivo)* | Opcional: `~/.config/jarvis-startup/config.json` con claves `titulo`, `project`, `theme`, `music_file`, `profile`. Prioridad: **env > config.json > perfil en código**. |
| `JARVIS_CONFIG_STRICT` | `1`: avisa en stderr por JSON inválido o claves desconocidas en `config.json`. |
| `JARVIS_DOCTOR_SKIP_NETWORK` | `1`: en `jarvis doctor` no intenta TCP a 1.1.1.1:443 (útil en CI o sin salida a Internet). |
| `JARVIS_PROFILE` | `default`, `taller`, `casa` — ajusta defaults de título y carpeta (si no sobreescribes `JARVIS_TITULO` / `JARVIS_NEW_PROJECT`). |
| `JARVIS_THEME` | `iron` (por defecto) o `minimal`. |
| `JARVIS_TITULO` | Cómo te nombra la voz (ej. tu apellido o “señor”). |
| `JARVIS_NEW_PROJECT` | Carpeta que abre Cursor. |
| `JARVIS_MUSIC_FILE` | Ruta al MP3 de fondo (por defecto `~/jarvis-startup/iron_music.mp3`). |
| `JARVIS_BOOT_SOUND` | Ruta opcional a `.wav` / `.ogg` corto, chime al inicio (estilo HUD); se reproduce en **dos canales** a volumen máximo para ganar ~+6 dB respecto a un solo canal. |
| `JARVIS_IDE_CHIME` | Ruta opcional a `.wav` / `.ogg` corto, tras abrir Cursor (antes de `wmctrl`). |
| `JARVIS_PRIVACY_MODE` | `1` / `true`: sin clima/red en saludo, sin hostname ni batería; frases más cortas (p. ej. pantalla compartida). |
| `JARVIS_MUSIC_FADE_IN_MS` | Entrada suave del MP3 (ms), por defecto `1200`; `0` = sin fade-in. |
| `JARVIS_MUSIC_FADEOUT_MS` | Salida suave al terminar (ms), por defecto `1200`; `0` = corte directo. |
| `JARVIS_TTS_VOICE` | Voz Edge (ej. `es-ES-AlvaroNeural`, `es-ES-ElviraNeural`). |
| `JARVIS_TTS_RATE` | Velocidad TTS, ej. `+10%` o `-5%`. |
| `JARVIS_MUSIC_VOLUME` | Volumen MP3 0.0–1.0 (por defecto `0.4375`). |
| `JARVIS_SKIP_NETWORK` | `1` / `true`: no consulta wttr.in. |
| `JARVIS_NO_NOTIFY` | `1` / `true`: no usa `notify-send`. |
| `JARVIS_DELAY_OPENCODE` | Segundos tras abrir terminal OpenCode (default `1.2`). |
| `JARVIS_DELAY_CURSOR` | Segundos tras Cursor (default `1.2`). |
| `JARVIS_DELAY_WMCTRL` | Espera antes de `wmctrl` (default `5`). |
| `JARVIS_CURSOR_BIN` / `JARVIS_OPENCODE_BIN` | Rutas a los ejecutables si no están en PATH. |
| `JARVIS_DRY_RUN` | `1` / `true`: mismo efecto que `--dry-run` (sin TTS, música, chime ni lanzar apps). |
| `JARVIS_USE_HOSTNAME` | Por defecto activo: añade «Unidad «hostname»» al saludo. `0` / `false` para omitir. |
| `JARVIS_USE_BATTERY` | Por defecto activo: si hay batería (`BAT*`), añade línea «Energía del reactor al X%». En torre suele no mostrar nada. |
| `JARVIS_SKIP_LAST_RUN_LOG` | `1` / `true`: no escribe `~/.local/share/jarvis-startup/last_run.json`. |
| `JARVIS_HUD` | `1` / `true`: al terminar la secuencia abre `hud_overlay.py` en ventana independiente (no en `--dry-run`). |
| `JARVIS_HUD_REFRESH_MS` | Intervalo de actualización del HUD (ms), por defecto `1500`. |
| `JARVIS_HUD_DURATION_SEC` | Si `>0`, cierra el HUD automáticamente tras esos segundos; `0` = hasta cerrar la ventana. |
| `JARVIS_HUD_FONT_SIZE` | Tamaño de fuente del HUD (por defecto `10`). |
| `JARVIS_HUD_HIDE_HOST` | `1`: oculta el hostname en la primera línea del HUD. |
| `JARVIS_HUD_UTC` | `1`: muestra hora en UTC con sufijo `UTC`. |
| `JARVIS_DIAG_DISK` | `1` / `true`: añade al segundo mensaje el uso de disco de `$HOME` (no en `JARVIS_PRIVACY_MODE`). |
| `JARVIS_DIAG_GIT` | `1` / `true`: añade rama y estado limpio/cambios si `JARVIS_GIT_DIR` o `JARVIS_NEW_PROJECT` es un repo git. |
| `JARVIS_GIT_DIR` | Carpeta del repo a inspeccionar (por defecto la misma que `JARVIS_NEW_PROJECT`). |
| `JARVIS_SECOND_PATH` | Segunda carpeta de proyecto: abre otra ventana de Cursor tras la primera (útil para comparar o dual-repo). |
| `JARVIS_NOTIFY_ICON` | Ruta a icono PNG/SVG para `notify-send -i` (si el archivo existe). |
| `JARVIS_REQUIRE_NETWORK` | `1` / `true`: si no hay conectividad (socket a 1.1.1.1:443), el script sale sin ejecutar la secuencia. |
| `JARVIS_REQUIRE_MONITOR` | `1` / `true`: si no hay `DISPLAY` ni `WAYLAND_DISPLAY`, sale (útil en autostart headless). |
| `JARVIS_LISTA_COMPLETA` | `1`: activa anexos de `jarvis_lista.py` en el saludo (diagnósticos ligeros, racha, etc.; respeta `JARVIS_PRIVACY_MODE`). |
| `JARVIS_FOCUS` / `JARVIS_EXPO` / `JARVIS_TEXT_ONLY` | Cualquiera a `1`: sin música de fondo, boot chime ni chime del IDE (presentación o solo consola). |
| `JARVIS_MARK_LEVEL` | `1`–`7`: factor de volumen del MP3 (vía `jarvis_lista.mark_music_volume_factor`). |
| `JARVIS_AUTOSTART_JITTER` | `1`: retraso aleatorio 0–2 s al inicio (menos picos si muchos autostarts). |
| `OLLAMA_HOST` / `JARVIS_OLLAMA_MODEL` | Opcional: si están definidos, `jarvis_lista` puede añadir una línea al anexo de saludo vía API local de Ollama. |
| `JARVIS_OPENING_PHRASE` | Texto impreso al inicio de la secuencia (antes del banner). |
| `JARVIS_CLOSING_PHRASE` | Texto tras «Secuencia completada»; con `JARVIS_CLOSING_TTS=1` también se habla con TTS. |
| `JARVIS_BANNER_FILE` | Ruta a archivo de texto/ASCII mostrado en consola al inicio. |
| `JARVIS_ANSI_BANNER` | Banner en línea (alternativa a archivo). |
| `JARVIS_ISOLATED_NOTICE` | `1`: añade aviso de modo aislado al anexo (solo texto). |
| `JARVIS_OPEN_README` | `1`: abre `README.md` del repo con `xdg-open` al final (no en dry-run). |
| `JARVIS_SCAN_SOUND` | Ruta a `.wav`/`.ogg` muy breve al calcular el saludo (volumen bajo). |
| `JARVIS_CHIME_SUCCESS` | Chime opcional tras completar la secuencia (antes de notify). |
| `JARVIS_TASKS_FILE` | JSON o Markdown con tareas; primera línea o ítem en anexo. |
| `JARVIS_ICS_FILE` | Ruta a `.ics` local; menciona evento próximo o aviso 15 min. |
| `JARVIS_GIT_STATUS_ANNEX` | `1`: incluye `git status -sb` en el anexo. |
| `JARVIS_TEST_CMD` | Comando shell para prueba (`bash -c`); solo se reporta código de salida. |
| `JARVIS_TEST_CMD_TIMEOUT` | Segundos máx. para `JARVIS_TEST_CMD` (default `60`). |
| `JARVIS_SKIP_UPDATES_CHECK` | `1`: no intenta detectar actualizaciones del sistema en el anexo. |
| `JARVIS_MISSIONS_FILE` | Primera línea no vacía se muestra en el HUD (idea 29). |
| `JARVIS_HUD_CPU_BAR` | `0`: oculta la barra de color por CPU en el HUD (default activo). |
| `JARVIS_NETWORK_NMCLI_FALLBACK` | `1` (default): si el socket a 1.1.1.1 falla, intenta `nmcli -t -f STATE g` = connected. `0` desactiva. |
| `JARVIS_MONITOR_XSET` | `1`: con `JARVIS_REQUIRE_MONITOR=1` y `DISPLAY`, exige `xset q` exit 0 (servidor X respondiendo). |
| `JARVIS_PCSPKR_BEEP` | `1`: en anexo intenta `beep` corto (paquete `beep` en sistema). |
| `JARVIS_OLLAMA_COMMIT_MSG` | `1`: con `OLLAMA_HOST` + `JARVIS_OLLAMA_MODEL` y repo git, sugiere mensaje de commit según `git diff --stat`. |
| `JARVIS_VOICE_CHAT_HINT` | `1`: añade línea al anexo y enlaza `contrib/README-voice-chat-hint.md`. |
| `JARVIS_FOCUS_WINDOWS_HINT` | `1`: recuerda usar compositor / `contrib/jarvis-window-hints.stub.sh` (no minimiza ventanas ajenas). |
| `JARVIS_GPG_RELEASE_HINT` | `1`: menciona `contrib/gpg-sign-release.example.sh` en anexo. |
| `JARVIS_PDF_PATHS` | Rutas `.pdf` separadas por `:` o `,`; se abren con `xdg-open` tras README (si existen archivos). |
| `JARVIS_SCREENSHOT_CONSENT` | `1`: requiere consentimiento explícito; captura con `grim` / `scrot` / `gnome-screenshot`. |
| `JARVIS_SCREENSHOT_DIR` | Directorio para capturas (default `~/.local/share/jarvis-startup/screenshots`). |
| `JARVIS_NOTIFY_START` | `1`: `notify-send` al iniciar la secuencia (antes del banner). |
| `JARVIS_CHIME_ERROR` | Ruta a `.wav`/`.ogg` si la secuencia falla con excepción (antes de relanzar error). |
| `JARVIS_LANG` | `es` o `en` para cadenas de consola traducidas (`_tr`); si vacío, se infiere de `LANG`. |
| `JARVIS_TTS_AUTO_LANG` | `1`: elige voz Edge según `LANG` (`JARVIS_TTS_VOICE_EN` / `JARVIS_TTS_VOICE_ES`). |
| `JARVIS_AUTOSTART_DELAY_SEC` | Entero (segundos): espera antes de ejecutar `./jarvis` cuando se usa [`scripts/jarvis_autostart.sh`](../scripts/jarvis_autostart.sh) (p. ej. autostart). `0` por defecto. |
| `JARVIS_AUTOSTART_LOG` | `1` (default): escribe salida en `~/.local/share/jarvis-startup/autostart.log` al usar `jarvis_autostart.sh`. `0` desactiva el log. |
| `JARVIS_AUTOSTART_INSTALL_DELAY` | Solo para [`scripts/install_xdg_autostart.sh`](../scripts/install_xdg_autostart.sh): segundos de retraso escritos en el `.desktop` (default `15`). |

Extensiones en `jarvis_lista.py` y documentos en `docs/` pueden añadir variables; esta tabla cubre el flujo principal.
