# Contribuir / despliegue local

- **Entorno:** [`install.sh`](../install.sh) crea `venv/` e instala `requirements.txt`.
- **Autostart XDG:** [`contrib/jarvis.desktop.example`](../contrib/jarvis.desktop.example) → `~/.config/autostart/`.
- **systemd --user:** [`contrib/jarvis-user.service.example`](../contrib/jarvis-user.service.example) (ajustar rutas).
- **Variables:** [`ENV.md`](ENV.md).
- **Pruebas:** `python -m unittest discover -s tests -v` desde la raíz del repo.
- **CI:** [`.github/workflows/jarvis.yml`](../.github/workflows/jarvis.yml).

Confirmación antes de comandos destructivos (idea 14): [`scripts/jarvis_confirm.py`](../scripts/jarvis_confirm.py).
