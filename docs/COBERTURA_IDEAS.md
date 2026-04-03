# Cobertura ítem a ítem (lista 1–100)

Referencia: [LISTA_IDEAS_COHERENTES_PELICULA.md](LISTA_IDEAS_COHERENTES_PELICULA.md).  
Leyenda: **Hecho** = implementado en código o script; **Parcial** = variable/flag o texto opcional; **No** = documentado como no implementado o solo doc; **Doc** = cubierto por documentación/contrib.

| # | Estado | Dónde / cómo |
|---|--------|----------------|
| 1 | Parcial | `JARVIS_THEME`, notificación final; `JARVIS_CLOSING_PHRASE` (v2.1) |
| 2 | Hecho | `JARVIS_RANDOM_OPENING`, variantes en `jarvis_lista.enhance_lines` |
| 3 | Hecho | `JARVIS_VOICE_MODE=militar` vs mayordomo |
| 4 | Hecho | `JARVIS_TITULO` en plantillas `bienvenido_jarvis` |
| 5 | Parcial | Saludo al abrir sesión; cierre vía `JARVIS_CLOSING_PHRASE` |
| 6 | Parcial | `JARVIS_TASKS_FILE`, `JARVIS_ICS_FILE` (v2.1) |
| 7 | Parcial | Mismo archivo de tareas / recordatorios |
| 8 | Parcial | `locale` sugerido en consola si voz por defecto; ver `docs/ENV.md` |
| 9 | Hecho | Subtítulos = líneas impresas antes de TTS |
| 10 | Hecho | `JARVIS_WITTY` |
| 11 | Hecho | `JARVIS_ENGINEER_QUOTE` |
| 12 | Hecho | `JARVIS_PRIVACY_MODE` |
| 13 | Parcial | `JARVIS_CLOSING_PHRASE` + TTS opcional al final |
| 14 | Hecho | [scripts/jarvis_confirm.py](../scripts/jarvis_confirm.py) |
| 15 | Hecho | `JARVIS_CODE_NAME` |
| 16 | Hecho | Boot + IDE chimes, música; capas vía env |
| 17 | Hecho | Ducking en `hablar` (volumen música) |
| 18 | Hecho | `JARVIS_MARK_LEVEL` + volumen |
| 19 | Hecho | `JARVIS_FOCUS` / `EXPO` / `TEXT_ONLY` |
| 20 | Parcial | `JARVIS_SCAN_SOUND` (v2.1) durante métricas |
| 21 | Doc | Normalización ffmpeg: doc en `contrib/README-normalize-audio.md` (v2.1) |
| 22 | Parcial | `JARVIS_CHIME_ERROR` / `SUCCESS` (v2.1) |
| 23 | No | PC speaker: no portable; ver sección H abajo |
| 24 | Hecho | `hud_overlay.py`, `JARVIS_HUD` |
| 25 | Hecho | Barra color CPU en HUD (`JARVIS_HUD_CPU_BAR`) v2.1 |
| 26 | Hecho | `JARVIS_NOTIFY_ICON` |
| 27 | Parcial | `JARVIS_ANSI_BANNER` / `JARVIS_BANNER_FILE` (v2.1) |
| 28 | Parcial | Mismo banner |
| 29 | Hecho | `JARVIS_MISSIONS_FILE` en HUD (v2.1) |
| 30 | Hecho | `JARVIS_HUD_HIDE_HOST` |
| 31 | No | Captura escritorio: H, privacidad |
| 32 | Hecho | CPU/RAM en saludo; disco en anexo/`DIAG_DISK` |
| 33 | Hecho | `_sn_temp` thermal_zone |
| 34 | Hecho | `_sn_net_iface` (v2.1) |
| 35 | Hecho | `_sn_ping_gateway` |
| 36 | Hecho | Batería `BAT*` en saludo |
| 37 | Hecho | `_sn_top3` |
| 38 | Hecho | `_sn_boot` |
| 39 | Hecho | `_sn_journal_err` |
| 40 | Hecho | `_sn_docker` |
| 41 | Hecho | `_sn_libvirt` |
| 42 | Parcial | `_sn_updates_pending` (v2.1) |
| 43 | Hecho | `JARVIS_INTEGRITY_FILE` / hash |
| 44 | Hecho | `_sn_tmp` |
| 45 | Hecho | `_sn_inodes_home` |
| 46 | Hecho | `JARVIS_ISOLATED_NOTICE` (v2.1) |
| 47 | Hecho | `_sn_vpn` |
| 48 | Hecho | `_sn_env_perms` |
| 49 | Hecho | `JARVIS_SECURITY_REMINDER_FILE`, `JARVIS_DEFAULT_2FA_REMINDER` |
| 50 | Hecho | `JARVIS_PROTOCOL_FILE` |
| 51 | No | gpg firmar release: manual / H |
| 52 | Hecho | Solo metadatos en anexos |
| 53 | Parcial | `DIAG_GIT`; `JARVIS_GIT_STATUS_ANNEX` (v2.1) |
| 54 | Hecho | `_sn_git_ahead` |
| 55 | Hecho | `_sn_branch_warn` |
| 56 | Hecho | `_sn_makefile` |
| 57 | Parcial | `JARVIS_TEST_CMD` código salida (v2.1) |
| 58 | Hecho | `JARVIS_OPEN_README` (v2.1) |
| 59 | Hecho | `JARVIS_BRIEFING_FILE` |
| 60 | Hecho | `JARVIS_SECOND_PATH` |
| 61 | Doc | Wayland/GNOME: README + lista |
| 62 | Hecho | Mensaje Wayland + `wmctrl` |
| 63 | Parcial | `wmctrl` geometría; multi-monitor manual |
| 64 | No | Minimizar todo salvo IDE: H |
| 65 | Hecho | `_sn_uptime_pause` |
| 66 | Parcial | `.ics` local opcional |
| 67 | Hecho | HUD UTC / local |
| 68 | Hecho | `_moon_phase` |
| 69 | Parcial | eventos `.ics` próximos 15 min |
| 70 | Hecho | `JARVIS_MARK_LEVEL` |
| 71 | Doc | Contador tests: variable futura / hooks |
| 72 | Hecho | `JARVIS_THERMAL_WARN` / frase térmica |
| 73 | Hecho | `JARVIS_EXPO` |
| 74 | No | Abrir PDFs al final: opcional futuro |
| 75 | Hecho | Sin logos Marvel; icono propio vía env |
| 76 | Parcial | `OLLAMA_HOST` + `JARVIS_OLLAMA_MODEL` |
| 77 | No | Commit message IA: H |
| 78 | No | Chat voz: H |
| 79 | Hecho | `contrib/jarvis-user.service.example` |
| 80 | Hecho | `JARVIS_AUTOSTART_JITTER` |
| 81 | Parcial | `JARVIS_REQUIRE_NETWORK` (socket); nmcli doc |
| 82 | Parcial | `JARVIS_REQUIRE_MONITOR`; xset doc |
| 83 | Hecho | `write_session_report` + last_run |
| 84 | Hecho | Rotación `last_run.json` |
| 85 | Hecho | `session_report.txt` |
| 86 | Parcial | `xrandr` / detección pantallas: doc |
| 87 | Hecho | `brightnessctl` frase |
| 88 | No | Bluetooth/sink: no por defecto |
| 89 | Parcial | `JARVIS_TEXT_ONLY` sin import pygame (v2.1) |
| 90 | No | i18n completo: fase futura |
| 91 | Hecho | `JARVIS_HUD_FONT_SIZE` |
| 92 | Hecho | `hooks.d/*.sh` |
| 93 | Hecho | [ENV.md](ENV.md) |
| 94 | Hecho | [CONTRIB.md](CONTRIB.md) |
| 95 | Hecho | `JARVIS_BIRTHDAY_MM_DD` |
| 96 | Hecho | `_streak_update` |
| 97 | Hecho | `_milestone_msg` |
| 98 | Parcial | Tests + mocks (v2.1) |
| 99 | Hecho | `.github/workflows/jarvis.yml` |
| 100 | Parcial | `install.sh`; pipx doc en CONTRIB |

## Ítems H / no implementados por defecto

| # | Motivo |
|---|--------|
| 23 | Beep altavoz interno: requiere permisos/pcspkr |
| 31 | Captura pantalla: privacidad |
| 51 | gpg release: flujo manual |
| 64 | Minimizar ventanas ajenas: WM específico |
| 74 | Biblioteca PDF: opt-in futuro |
| 77–78 | IA diff/chat voz: alcance producto |
| 88 | Bluetooth/pipewire: dependencia distro |

## Enlaces

- Variables: [ENV.md](ENV.md)
- Contribución: [CONTRIB.md](CONTRIB.md)
