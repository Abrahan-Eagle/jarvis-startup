#!/usr/bin/env python3
"""HUD minimal estilo taller: hora, hostname, CPU (y RAM). Proceso independiente.

Requiere: python3-tk, psutil (mismo venv que Jarvis).

Ideas 25 / 29: barra de color por umbral de CPU y línea de misiones opcional.
"""

from __future__ import annotations

import datetime
import os
import socket
import sys


def _cpu_color(cpu: int) -> str:
    if cpu < 50:
        return "#00c853"
    if cpu < 80:
        return "#ffab00"
    return "#ff5252"


def _load_missions_line() -> str:
    fp = os.getenv("JARVIS_MISSIONS_FILE", "").strip()
    if not fp:
        return ""
    p = os.path.expanduser(fp)
    if not os.path.isfile(p):
        return ""
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln in f:
                s = ln.strip()
                if s and not s.startswith("#"):
                    return s[:120]
    except OSError:
        pass
    return ""


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
    show_bar = os.getenv("JARVIS_HUD_CPU_BAR", "1").strip().lower() not in ("0", "false", "no", "off")
    missions = _load_missions_line()

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
    w, h = 320, 110 if (missions or show_bar) else 88
    if missions:
        h += 18
    x = max(8, sw - w - 20)
    y = 20
    root.geometry(f"{w}x{h}+{x}+{y}")

    fg = "#00e5cc"
    bg = "#0d1117"
    try:
        font = ("DejaVu Sans Mono", font_size)
    except tk.TclError:
        font = ("Courier", font_size)

    frm = tk.Frame(root, bg=bg)
    frm.pack(fill=tk.BOTH, expand=True)

    mission_lbl = None
    if missions:
        mission_lbl = tk.Label(
            frm,
            text=f"⚙ {missions}",
            justify=tk.LEFT,
            fg="#8be9fd",
            bg=bg,
            font=(font[0], max(6, font_size - 2)),
            padx=10,
            pady=(4, 0),
        )
        mission_lbl.pack(fill=tk.X)

    lbl = tk.Label(frm, text="", justify=tk.LEFT, fg=fg, bg=bg, font=font, padx=10, pady=6)
    lbl.pack(fill=tk.BOTH, expand=True)

    bar_canvas = None
    bar_w = w - 20
    if show_bar:
        bar_canvas = tk.Canvas(frm, height=6, bg=bg, highlightthickness=0, bd=0)
        bar_canvas.pack(fill=tk.X, padx=10, pady=(0, 6))

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
        if bar_canvas is not None:
            bar_canvas.delete("all")
            col = _cpu_color(cpu)
            fill_w = max(2, int(bar_w * min(100, cpu) / 100.0))
            bar_canvas.create_rectangle(0, 0, fill_w, 8, fill=col, outline=col)
            bar_canvas.create_rectangle(0, 0, bar_w, 8, outline="#30363d")
        root.after(refresh, tick)

    tick()
    if duration_ms > 0:
        root.after(duration_ms, root.destroy)

    root.mainloop()


if __name__ == "__main__":
    main()
