# Contribuir / despliegue local

- **Entorno:** [`install.sh`](../install.sh) crea `venv/` e instala `requirements.txt`.
- **Autostart XDG:** [`contrib/jarvis.desktop.example`](../contrib/jarvis.desktop.example) → `~/.config/autostart/`.
- **systemd --user:** [`contrib/jarvis-user.service.example`](../contrib/jarvis-user.service.example) (ajustar rutas).
- **Variables:** [`ENV.md`](ENV.md).
- **Pruebas:** `python -m unittest discover -s tests -v` desde la raíz del repo.
- **CI:** [`.github/workflows/jarvis.yml`](../.github/workflows/jarvis.yml).

Confirmación antes de comandos destructivos (idea 14): [`scripts/jarvis_confirm.py`](../scripts/jarvis_confirm.py).

- Normalización de audio offline (idea 21): [`README-normalize-audio.md`](../contrib/README-normalize-audio.md).
- Reglas de ventana / compositor (ideas 61, 63): [`jarvis-window-hints.stub.sh`](../contrib/jarvis-window-hints.stub.sh) (plantilla; no automatiza el escritorio).
- Chat voz + IA externa (idea 78): [`README-voice-chat-hint.md`](../contrib/README-voice-chat-hint.md).
- Firma GPG de releases (idea 51): [`gpg-sign-release.example.sh`](../contrib/gpg-sign-release.example.sh).
