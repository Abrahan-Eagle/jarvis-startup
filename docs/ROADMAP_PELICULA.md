# Roadmap estilo Iron Man — Jarvis local (`~/jarvis-startup`)

Priorización de **10 mejoras** alineadas con la película (mayordomo, diagnósticos, ritual del taller). Esfuerzo: **S** = pocas horas, **M** = 1–2 días, **L** = varios días o depende del entorno.

Todas son **solo este repo** (sin Zonix Eats).

| # | Mejora | Esfuerzo | Idea origen (lista 50) | Estado |
|---|--------|----------|-------------------------|--------|
| 1 | **`--dry-run` + `JARVIS_DRY_RUN`** — simular secuencia sin TTS, audio ni apps | **S** | 39 | ✅ v1.3.0 |
| 2 | **Log `~/.local/share/jarvis-startup/last_run.json`** — timestamp, versión, modo dry | **S** | 38 | ✅ v1.3.0 |
| 3 | **Diagnóstico “reactor”** — batería vía sysfs si hay `BAT*` | **S** | 6 | ✅ v1.3.0 (`JARVIS_USE_BATTERY`) |
| 4 | **Unidad / hostname** en el saludo (opcional, env) | **S** | 28 | ✅ v1.3.0 (`JARVIS_USE_HOSTNAME`) |
| 5 | **Chime por fase** — segundo sonido al abrir IDE (env separado) | **M** | 13 | ✅ v1.4.0 (`JARVIS_IDE_CHIME`) |
| 6 | **Fade-in/out música** — menos brusco que play/stop | **M** | 14 | ✅ v1.4.0 |
| 7 | **Modo “congreso”** — frases cortas, sin clima (`JARVIS_PRIVACY_MODE`) | **M** | 17 | ✅ v1.4.0 |
| 8 | **Detección Wayland** — mensaje claro si `wmctrl` no aplica | **M** | 37 | ✅ v1.4.0 |
| 9 | **HUD overlay minimal** (tkinter/pyqt) — hora + CPU en esquina | **L** | 23 | ✅ v1.5.0 (`hud_overlay.py`, `JARVIS_HUD`) |
| 10 | **Fallback voz offline** (`espeak-ng`) si Edge falla | **M** | 44 | ✅ v1.4.0 |

## Ya implementado (referencia)

- Música configurable (`JARVIS_MUSIC_FILE`), chime HUD (`JARVIS_BOOT_SOUND`, doble canal).
- Perfiles, temas `iron` / `minimal`, TTS Edge, notificación, layout con `wmctrl`.
- v1.3.0: `--dry-run`, log `last_run.json`, batería + hostname en saludo.
- v1.4.0: `JARVIS_IDE_CHIME`, `JARVIS_PRIVACY_MODE`, fade música, aviso Wayland, respaldo `espeak-ng`/`espeak`.
- v1.5.0: HUD `hud_overlay.py`, diagnósticos opcionales disco/Git (`JARVIS_DIAG_*`).

## Backlog (resto de la lista 50)

Ideas no priorizadas en el top 10: protocolos numerados, Mark X, temperatura CPU, espacio disco, Git status, Docker, VPN, systemd user unit, empaquetado pipx, script de despedida, etc. — ver mensaje de planificación original o ampliar este documento por iteración.

**Última actualización:** 2026-04-03
