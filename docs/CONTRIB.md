# Contribuir / despliegue local

- **Entorno:** [`install.sh`](../install.sh) crea `venv/` e instala `requirements.txt`.
- **Autostart al iniciar sesión:** [`scripts/jarvis_autostart.sh`](../scripts/jarvis_autostart.sh) — retraso opcional (`JARVIS_AUTOSTART_DELAY_SEC`), log opcional (`JARVIS_AUTOSTART_LOG`). Plantillas: [`jarvis.desktop.example`](../contrib/jarvis.desktop.example) → `~/.config/autostart/`, [`jarvis-user.service.example`](../contrib/jarvis-user.service.example) (systemd --user; ajustar rutas).
- **Variables:** [`ENV.md`](ENV.md).
- **Config JSON:** `~/.config/jarvis-startup/config.json` — `titulo`, `project`, `theme`, `music_file`, `profile` (ver README); precedencia por encima del perfil embebido y por debajo del entorno.
- **Pruebas:** `python -m unittest discover -s tests -v` desde la raíz del repo.
- **CI:** [`.github/workflows/jarvis.yml`](../.github/workflows/jarvis.yml).

Confirmación antes de comandos destructivos (idea 14): [`scripts/jarvis_confirm.py`](../scripts/jarvis_confirm.py).

- Normalización de audio offline (idea 21): [`README-normalize-audio.md`](../contrib/README-normalize-audio.md).
- Reglas de ventana / compositor (ideas 61, 63): [`jarvis-window-hints.stub.sh`](../contrib/jarvis-window-hints.stub.sh) (plantilla; no automatiza el escritorio).
- Chat voz + IA externa (idea 78): [`README-voice-chat-hint.md`](../contrib/README-voice-chat-hint.md).
- Firma GPG de releases (idea 51): [`gpg-sign-release.example.sh`](../contrib/gpg-sign-release.example.sh).
