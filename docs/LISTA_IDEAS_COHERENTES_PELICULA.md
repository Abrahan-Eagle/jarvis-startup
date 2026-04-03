# Ideas coherentes con Jarvis en las películas *Iron Man* / MCU

Referencia creativa para el proyecto local (`~/jarvis`). **No** es copia de guiones ni de Marvel; es el *tipo* de cosas que el asistente hace en pantalla: mayordomo técnico, diagnósticos, ritual del laboratorio, capas de “sistemas”. Muchas son viables en Linux con scripts; otras son aspiracionales (IA, hardware dedicado).

**Alcance:** exactamente **100** ideas numeradas (1–100); el resto se prioriza en sprints aparte.

**Leyenda de viabilidad (orientativa):** `L` = script/local, `M` = integración media, `H` = alto esfuerzo o depende de terceros.

---

## Voz, diálogo y personalidad

1. Frases de confirmación breves tras acciones (“Hecho, señor.” / “Listo.”) — `L`
2. Variantes aleatorias de saludo para no sonar repetitivo — `L`
3. Modo “mayordomo” vs modo “briefing militar” (dos vocabularios) — `L`
4. Uso consistente del tratamiento configurado (`JARVIS_TITULO`) en plantillas — `L`
5. Líneas de “estado del taller” al abrir/cerrar sesión — `L`
6. Resumen en una frase del plan del día (si hay calendario local) — `M`
7. Recordatorios hablados de tareas (lista en archivo Markdown/JSON) — `M`
8. Detección de idioma del sistema y voz TTS alineada — `L`
9. Subtítulos en consola sincronizados con lo que diría la voz — `L`
10. “Modo cínico suave” opcional (humor seco, sin cruzar línea ofensiva) — `L`
11. Citas *inventadas* estilo ingeniero (“Integridad estructural nominal”) — `L`
12. Evitar datos médicos personales en saludos (privacidad) — `L`
13. Frase de cierre al apagar o cerrar IDE — `L`
14. Confirmación por voz antes de acciones destructivas (script aparte) — `M`
15. Nombre en clave del proyecto en curso (variable de entorno) — `L`

## Audio y ambiente

16. Capas de sonido: arranque, transición, “sistemas listos”, cierre — `L`
17. Ducking automático voz vs música (ya parcialmente) — `L`
18. Perfil “sala de pruebas” con música más contenida — `L`
19. Silencio total excepto chimes en modo “focus” — `L`
20. Sonido tipo “escaneo” muy bajo durante lectura de métricas — `M`
21. Normalización de volumen entre assets (ffmpeg offline) — `M`
22. Biblioteca de chimes por evento (boot, IDE, error, éxito) — `L`
23. Vibración / haptic no aplica en desktop; en laptop: beep PC speaker opcional — `H`

## HUD, visual y “capas” en pantalla

24. Overlay mínimo: hora + CPU + hostname (tkinter transparente o `yad`) — `M` — **Implementado** en v1.5.0 como [`hud_overlay.py`](../hud_overlay.py) con `JARVIS_HUD=1` (hora, hostname, CPU y RAM).
25. Barra fina tipo “estado de sistemas” con color por umbral CPU — `M`
26. Notificación con icono personal estilo arco/reactor — `L`
27. Tema de colores ANSI en terminal (verde/cyan “terminal clásica”) — `L`
28. Banner ASCII del nombre del taller — `L`
29. Widget de “misiones” del día (texto estático refrescado) — `M`
30. Modo “presentación”: ocultar hostname/IP en overlay — `L`
31. Captura de “foto del escritorio” solo para log local (opcional, con consentimiento) — `H`

## Diagnósticos y “sistemas”

32. CPU, RAM, disco (por partición o `$HOME`) — `L`
33. Temperatura CPU/GPU si hay `sensors` o sysfs — `L`
34. Carga de red (interfaz activa) — `M`
35. Ping a gateway o DNS como “enlace” — `L`
36. Batería y estado AC (ya parcial) — `L`
37. Lista de procesos que más CPU consumen (top 3 en frase) — `L`
38. Último arranque del sistema (`who -b` / journal) — `L`
39. Errores recientes del kernel (últimas líneas `journalctl -p err`) — `M`
40. Estado de Docker (contadores) — `L`
41. Estado de VMs (libvirt) si existe — `M`
42. Comprobar actualizaciones pendientes (apt/dnf/pacman según distro) — `M`
43. Hash rápido de un archivo como “prueba de integridad” simbólica — `L`
44. Chequeo de espacio en `/tmp` — `L`
45. Inodos libres en partición crítica — `L`

## Red, seguridad y “protocolos”

46. Modo “aislado”: sin tráfico saliente opcional (firewall ya es manual; aviso solo) — `L`
47. Detectar interfaz VPN/tun y mencionarlo — `L`
48. Aviso si hay `.env` con permisos demasiado abiertos — `L`
49. Recordatorio de rotar claves / 2FA (texto estático configurable) — `L`
50. “Protocolo de laboratorio”: checklist hablado antes de demo (script) — `L`
51. Integración con `gpg` para firmar un artefacto de release — `M`
52. No leer ni enviar secretos; solo metadatos — `L`

## Taller, proyectos y flujo de trabajo

53. Abrir repo Git en Cursor en rama actual con resumen `git status -sb` — `L`
54. Decir en voz cuántos commits por delante/atras de `origin` — `L`
55. Recordar rama si no es `main`/`dev` — `L`
56. Detectar `Makefile`/`justfile` y sugerir objetivo por defecto — `M`
57. Lanzar tests con un comando configurable y leer solo código de salida — `M`
58. Abrir documentación local (`README.md`) en visor — `L`
59. Plantilla de “briefing” del proyecto en `~/jarvis/briefing.md` leído en voz — `L`
60. Segundo proyecto en ventana (split) si variable `JARVIS_SECOND_PATH` — `M`

## Ventanas, escritorio y sesión

61. Reglas por compositor (GNOME/KDE) en lugar de solo `wmctrl` — `M`
62. Detección Wayland y mensaje (ya parcial) — `L`
63. Posicionar ventanas por porcentaje de pantalla (multi-monitor) — `M`
64. “Modo foco”: minimizar todo excepto IDE — `H`
65. Recordatorio de pausa larga si uptime > N horas — `L`

## Calendario, tiempo y contexto

66. Integración con `gcalcli` o archivo `.ics` local — `M`
67. Hora local y UTC en overlay — `L`
68. Fase lunar o broma astronómica ligera — `L`
69. Recordatorio de reuniones en los próximos 15 min — `M`

## Iron Man / MCU (metáforas seguras, sin IP ajenas)

70. Niveles de “Mark” como perfiles de potencia (Mark 1 = mínimo, Mark 7 = todo on) — `L`
71. Contador de “pruebas de campo” (cada vez que pasas tests) en archivo — `L`
72. Frase al superar umbral de carga: “Sobrecarga térmica simulada” — `L`
73. Modo “expo” con frases más cortas y sin música — `L`
74. “Biblioteca de diseños”: rutas a PDFs de referencia abiertos al final — `M`
75. Nada de imágenes/logos oficiales de Marvel; icono propio o libre — `L`

## Integración futura con IA (opcional)

76. Resumen del diff de `git` por modelo local (Ollama) — `H`
77. Sugerencia de commit message desde diff — `H`
78. Chat por voz con backend local — `H`

## Automatización y arranque

79. Unidad systemd user para ejecutar al login — `L`
80. Retraso aleatorio pequeño para no competir con otros autostarts — `L`
81. Condición: solo si hay red (NetworkManager `nmcli`) — `M`
82. Condición: solo si monitor encendido (`xset q` / logind) — `M`

## Datos, logs y telemetría local

83. Log JSON por ejecución enriquecido (versión, tiempos por fase) — `L`
84. Rotación de logs por tamaño — `L`
85. Exportar “informe de sesión” en TXT al final — `L`

## Hardware y periféricos

86. Detectar si hay segundo monitor — `M`
87. Brillo de pantalla (`brightnessctl`) en frase — `L`
88. Estado de Bluetooth/audio sink por defecto — `M`

## Accesibilidad y UX

89. Modo solo texto (sin pygame) para entornos mínimos — `M`
90. Salida traducible (ficheros `es`/`en`) — `M`
91. Tamaño de fuente del overlay configurable — `L`

## Comunidad y extensión

92. Plugins: carpeta `~/.config/jarvis/hooks.d/` con scripts ejecutados en orden — `M`
93. Variables de entorno documentadas en un solo `ENV.md` — `L`
94. Plantilla de contribución para nuevos “protocolos” — `L`

## Ocio y easter eggs (sin infringir derechos)

95. Mensaje especial en tu cumpleaños (fecha en env) — `L`
96. Contador de “días consecutivos” usando el proyecto — `L`
97. Frase si la fecha coincide con un hito histórico de la ingeniería (lista local) — `L`

## Calidad y mantenimiento

98. Tests unitarios con mocks de red y pygame — `M`
99. CI en GitHub Actions solo `py_compile` + dry-run — `L`
100. Empaquetado `pipx` o script de instalación — `M`

---

## Cobertura v2.0 (implementación agregada)

No hay un archivo por idea: el conjunto **1–100** queda cubierto por `bienvenido_jarvis.py` + `jarvis_lista.py` + `hud_overlay.py`, variables en [`ENV.md`](ENV.md), anexos de saludo con `JARVIS_LISTA_COMPLETA`, hooks (`run_hooks` → `~/.config/jarvis/hooks.d/`), informe de sesión, CI (`.github/workflows/jarvis.yml`), tests (`tests/`), `install.sh`, [`scripts/jarvis_confirm.py`](../scripts/jarvis_confirm.py), y ejemplos en `contrib/`. Las ideas marcadas `H` o dependientes de hardware ajeno siguen siendo aspiracionales.

---

## Cómo usar esta lista

- Elige **3–5** ítems por sprint; muchos `L` se pueden encadenar en una tarde.  
- Lo que toque **red, APIs o IA** marca como `M`/`H` y conviene diseñar antes (privacidad, límites).  
- Mantén la coherencia con el tono: **asistente del taller**, no sustituto de decisiones críticas de seguridad.

**Última actualización:** 2026-04-02 — lista acotada a 100 ítems; nota de cobertura v2.0 arriba.
