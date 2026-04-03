# Normalizar volumen entre assets (idea 21)

Jarvis no incluye `ffmpeg` como dependencia. Para igualar niveles entre chimes y música de fondo, procesa los archivos localmente:

```bash
ffmpeg -i entrada.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 salida.wav
```

Ajuste `I` según tu preferencia (–16 LUFS es un punto de partida razonable para efectos cortos).
