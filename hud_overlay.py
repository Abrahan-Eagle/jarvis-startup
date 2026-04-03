#!/usr/bin/env python3
"""HUD minimal estilo taller: hora, hostname, CPU (y RAM). Proceso independiente.

Requiere: python3-tk, psutil (mismo venv que Jarvis).
"""

from __future__ import annotations

import datetime
import os
import socket
import sys


def main() -> None:
    try:
        import tkinter as tk
    except ImportError:
        print("tkinter no disponible; instala el paquete python3-tk.", file=sys.stderr)
        sys.exit(1)

    import psutil

    refresh = max(400, int(os.getenv("JARVIS_HUD_REFRESH_MS", "1500")))
    duration_ms = max(0, int(os.getenv("JARVIS_HUD_DURATION_SEC", "0"))) * 1000
    try:
        font_size = max(6, min(28, int(os.getenv("JARVIS_HUD_FONT_SIZE", "10"))))
    except ValueError:
        font_size = 10
    hide_host = os.getenv("JARVIS_HUD_HIDE_HOST", "").strip().lower() in ("1", "true", "yes", "on")
    use_utc = os.getenv("JARVIS_HUD_UTC", "").strip().lower() in ("1", "true", "yes", "on")

    try:
        hn = socket.gethostname().split(".")[0]
    except OSError:
        hn = "?"

    root = tk.Tk()
    root.title("Jarvis HUD")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-alpha", 0.88)
    except tk.TclError:
        pass

    sw = root.winfo_screenwidth()
    w, h = 300, 88
    x = max(8, sw - w - 20)
    y = 20
    root.geometry(f"{w}x{h}+{x}+{y}")

    fg = "#00e5cc"
    bg = "#0d1117"
    try:
        font = ("DejaVu Sans Mono", font_size)
    except tk.TclError:
        font = ("Courier", font_size)

    lbl = tk.Label(root, text="", justify=tk.LEFT, fg=fg, bg=bg, font=font, padx=10, pady=6)
    lbl.pack(fill=tk.BOTH, expand=True)

    def tick() -> None:
        if use_utc:
            now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
        else:
            now = datetime.datetime.now().strftime("%H:%M:%S")
        cpu = int(psutil.cpu_percent(interval=None))
        mem = int(psutil.virtual_memory().percent)
        if hide_host:
            line1 = now
        else:
            line1 = f"{now}  ·  {hn}"
        lbl.config(text=f"{line1}\nCPU {cpu}%   RAM {mem}%")
        root.after(refresh, tick)

    tick()
    if duration_ms > 0:
        root.after(duration_ms, root.destroy)

    root.mainloop()


if __name__ == "__main__":
    main()
