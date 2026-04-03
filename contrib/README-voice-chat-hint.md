# Chat de voz con IA (idea 78)

Jarvis no incorpora un cliente de voz completo: el flujo principal es bienvenida + TTS + entorno.

Para experimentar **chat por voz** con un modelo local:

1. Instale [Ollama](https://ollama.com/) y un modelo compatible.
2. Use un cliente que una **STT** (voz→texto) + API HTTP de Ollama + **TTS** (texto→voz), o un asistente de escritorio que ya integre micrófono.
3. Opcional: exponga `OLLAMA_HOST` y fije `JARVIS_OLLAMA_MODEL` para que el anexo de saludo pueda mostrar una frase generada (ver `docs/ENV.md`).

No se graba audio desde `bienvenido_jarvis.py` salvo que active explícitamente otras herramientas en su sistema.
