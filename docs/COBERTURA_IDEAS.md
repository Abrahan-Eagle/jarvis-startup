# Cobertura ítem a ítem (lista 1–100)

Referencia: [LISTA_IDEAS_COHERENTES_PELICULA.md](LISTA_IDEAS_COHERENTES_PELICULA.md).  
Leyenda: **Hecho** = implementado en código, script o documentación enlazada desde el repo.

| # | Estado | Dónde / cómo |
|---|--------|----------------|
| 1 | Hecho | `JARVIS_NOTIFY_START` + `notify-send` al inicio; tema en cuerpo |
| 2 | Hecho | `JARVIS_RANDOM_OPENING`, variantes en `jarvis_lista.enhance_lines` |
| 3 | Hecho | `JARVIS_VOICE_MODE=militar` vs mayordomo |
| 4 | Hecho | `JARVIS_TITULO` en plantillas `bienvenido_jarvis` |
| 5 | Hecho | `JARVIS_OPENING_PHRASE`; cierre `JARVIS_CLOSING_PHRASE` + TTS opcional (`JARVIS_CLOSING_TTS`) |
| 6 | Hecho | `JARVIS_TASKS_FILE` en anexo |
| 7 | Hecho | Mismo archivo de tareas / recordatorios (`JARVIS_TASKS_FILE`) |
| 8 | Hecho | `JARVIS_TTS_AUTO_LANG` + `JARVIS_TTS_VOICE_EN` / `JARVIS_TTS_VOICE_ES`; consola en `mostrar_config` |
| 9 | Hecho | Subtítulos = líneas impresas antes de TTS |
| 10 | Hecho | `JARVIS_WITTY` |
| 11 | Hecho | `JARVIS_ENGINEER_QUOTE` |
| 12 | Hecho | `JARVIS_PRIVACY_MODE` |
| 13 | Hecho | `JARVIS_CLOSING_PHRASE` + `JARVIS_CLOSING_TTS` |
| 14 | Hecho | [scripts/jarvis_confirm.py](../scripts/jarvis_confirm.py) |
| 15 | Hecho | `JARVIS_CODE_NAME` |
| 16 | Hecho | Boot + IDE chimes, música; capas vía env |
| 17 | Hecho | Ducking en `hablar` (volumen música) |
| 18 | Hecho | `JARVIS_MARK_LEVEL` + volumen |
| 19 | Hecho | `JARVIS_FOCUS` / `EXPO` / `TEXT_ONLY` |
| 20 | Hecho | `JARVIS_SCAN_SOUND` durante métricas |
| 21 | Hecho | Normalización ffmpeg: [contrib/README-normalize-audio.md](../contrib/README-normalize-audio.md) |
| 22 | Hecho | `JARVIS_CHIME_SUCCESS` / `JARVIS_CHIME_ERROR` (v2.2) |
| 23 | Hecho | `JARVIS_PCSPKR_BEEP` + comando `beep` opcional |
| 24 | Hecho | `hud_overlay.py`, `JARVIS_HUD` |
| 25 | Hecho | Barra color CPU en HUD (`JARVIS_HUD_CPU_BAR`) |
| 26 | Hecho | `JARVIS_NOTIFY_ICON` |
| 27 | Hecho | `JARVIS_ANSI_BANNER` / `JARVIS_BANNER_FILE` |
| 28 | Hecho | Mismo banner (archivo o inline) |
| 29 | Hecho | `JARVIS_MISSIONS_FILE` en HUD |
| 30 | Hecho | `JARVIS_HUD_HIDE_HOST` |
| 31 | Hecho | `JARVIS_SCREENSHOT_CONSENT` + `grim`/`scrot`/`gnome-screenshot` + `JARVIS_SCREENSHOT_DIR` |
| 32 | Hecho | CPU/RAM en saludo; disco en anexo/`DIAG_DISK` |
| 33 | Hecho | `_sn_temp` thermal_zone |
| 34 | Hecho | `_sn_net_iface` |
| 35 | Hecho | `_sn_ping_gateway` |
| 36 | Hecho | Batería `BAT*` en saludo |
| 37 | Hecho | `_sn_top3` |
| 38 | Hecho | `_sn_boot` |
| 39 | Hecho | `_sn_journal_err` |
| 40 | Hecho | `_sn_docker` |
| 41 | Hecho | `_sn_libvirt` |
| 42 | Hecho | `_sn_updates_pending` |
| 43 | Hecho | `JARVIS_INTEGRITY_FILE` / hash |
| 44 | Hecho | `_sn_tmp` |
| 45 | Hecho | `_sn_inodes_home` |
| 46 | Hecho | `JARVIS_ISOLATED_NOTICE` |
| 47 | Hecho | `_sn_vpn` |
| 48 | Hecho | `_sn_env_perms` |
| 49 | Hecho | `JARVIS_SECURITY_REMINDER_FILE`, `JARVIS_DEFAULT_2FA_REMINDER` |
| 50 | Hecho | `JARVIS_PROTOCOL_FILE` |
| 51 | Hecho | `JARVIS_GPG_RELEASE_HINT` + [contrib/gpg-sign-release.example.sh](../contrib/gpg-sign-release.example.sh) |
| 52 | Hecho | Solo metadatos en anexos |
| 53 | Hecho | `DIAG_GIT`; `JARVIS_GIT_STATUS_ANNEX` |
| 54 | Hecho | `_sn_git_ahead` |
| 55 | Hecho | `_sn_branch_warn` |
| 56 | Hecho | `_sn_makefile` |
| 57 | Hecho | `JARVIS_TEST_CMD` + contador en `field_tests.json` |
| 58 | Hecho | `JARVIS_OPEN_README` |
| 59 | Hecho | `JARVIS_BRIEFING_FILE` |
| 60 | Hecho | `JARVIS_SECOND_PATH` |
| 61 | Hecho | Wayland/GNOME: README + lista |
| 62 | Hecho | Mensaje Wayland + `wmctrl` |
| 63 | Hecho | `wmctrl` + anexo xrandr (pantallas); [jarvis-window-hints.stub.sh](../contrib/jarvis-window-hints.stub.sh) |
| 64 | Hecho | `JARVIS_FOCUS_WINDOWS_HINT` + contrib |
| 65 | Hecho | `_sn_uptime_pause` |
| 66 | Hecho | `JARVIS_ICS_FILE` |
| 67 | Hecho | HUD UTC / local |
| 68 | Hecho | `_moon_phase` |
| 69 | Hecho | eventos `.ics` próximos 15 min en `_sn_ics_reminder` |
| 70 | Hecho | `JARVIS_MARK_LEVEL` |
| 71 | Hecho | Contador `~/.local/share/jarvis-startup/field_tests.json` al éxito de `JARVIS_TEST_CMD` |
| 72 | Hecho | `JARVIS_THERMAL_WARN` / frase térmica |
| 73 | Hecho | `JARVIS_EXPO` |
| 74 | Hecho | `JARVIS_PDF_PATHS` + `xdg-open` |
| 75 | Hecho | Sin logos Marvel; icono propio vía env |
| 76 | Hecho | `OLLAMA_HOST` + `JARVIS_OLLAMA_MODEL` + `_ollama_line` |
| 77 | Hecho | `JARVIS_OLLAMA_COMMIT_MSG` + `git diff --stat` vía Ollama |
| 78 | Hecho | `JARVIS_VOICE_CHAT_HINT` + [README-voice-chat-hint.md](../contrib/README-voice-chat-hint.md) |
| 79 | Hecho | `contrib/jarvis-user.service.example` |
| 80 | Hecho | `JARVIS_AUTOSTART_JITTER` |
| 81 | Hecho | `JARVIS_REQUIRE_NETWORK` + socket; `JARVIS_NETWORK_NMCLI_FALLBACK` + `nmcli` |
| 82 | Hecho | `JARVIS_REQUIRE_MONITOR` + `JARVIS_MONITOR_XSET` + `xset q` |
| 83 | Hecho | `write_session_report` + last_run |
| 84 | Hecho | Rotación `last_run.json` |
| 85 | Hecho | `session_report.txt` |
| 86 | Hecho | `_sn_xrandr_monitors` |
| 87 | Hecho | `brightnessctl` frase |
| 88 | Hecho | `_sn_pactl_audio` (`pactl get-default-sink`) |
| 89 | Hecho | `JARVIS_TEXT_ONLY` sin import pygame |
| 90 | Hecho | `JARVIS_LANG` / `LANG` + cadenas `_tr()` en flujo principal |
| 91 | Hecho | `JARVIS_HUD_FONT_SIZE` |
| 92 | Hecho | `hooks.d/*.sh` |
| 93 | Hecho | [ENV.md](ENV.md) |
| 94 | Hecho | [CONTRIB.md](CONTRIB.md) |
| 95 | Hecho | `JARVIS_BIRTHDAY_MM_DD` |
| 96 | Hecho | `_streak_update` |
| 97 | Hecho | `_milestone_msg` |
| 98 | Hecho | Tests + mocks en `tests/` |
| 99 | Hecho | `.github/workflows/jarvis.yml` |
| 100 | Hecho | `install.sh` + pista `pipx` en salida; CONTRIB |

## Ítems H / no implementados por defecto

*(vacío en v2.2 — todo tiene ruta de implementación o documentación explícita.)*

## Enlaces

- Variables: [ENV.md](ENV.md)
- Contribución: [CONTRIB.md](CONTRIB.md)
