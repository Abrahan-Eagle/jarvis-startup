# Autostart: no corre al reiniciar / al iniciar sesión

## Comprobaciones rápidas

1. **Instalación recomendada (rutas correctas)**  
   Desde la raíz del repo:
   ```bash
   ./scripts/install_xdg_autostart.sh
   ```
   Eso crea `~/.config/autostart/jarvis-bienvenida.desktop` con rutas absolutas y `chmod +x` en `jarvis` y `jarvis_autostart.sh`.

2. **Permisos**
   ```bash
   chmod +x jarvis scripts/jarvis_autostart.sh
   ```

3. **Log**  
   Si `JARVIS_AUTOSTART_LOG=1` (por defecto en el instalador), mira:
   ```text
   ~/.local/share/jarvis-startup/autostart.log
   ```
   Si el archivo no existe tras un login, el `.desktop` no se ejecutó (ruta mala, autostart desactivado en el escritorio, o sesión no gráfica).

4. **GNOME / “Aplicaciones al inicio”**  
   Abre *Aplicaciones al inicio* (Startup Applications) y comprueba que *Jarvis Bienvenida* esté activada.

5. **Probar sin reiniciar**
   ```bash
   gtk-launch jarvis-bienvenida
   ```
   Si falla, el error suele verse en la terminal o en `autostart.log`.

6. **Reinicio vs cerrar sesión**  
   Tras un reinicio completo, a veces la red o el escritorio tardan; el instalador pone `JARVIS_AUTOSTART_DELAY_SEC=15` y `X-GNOME-Autostart-Delay`. Puedes subir el retraso:
   ```bash
   JARVIS_AUTOSTART_INSTALL_DELAY=25 ./scripts/install_xdg_autostart.sh
   ```

7. **Variables que abortan la secuencia**  
   Si exportaste `JARVIS_REQUIRE_NETWORK=1` o `JARVIS_REQUIRE_MONITOR=1` en un sitio global y al login aún no hay red o sesión gráfica lista, Jarvis puede salir sin hacer nada. Revisa el log o prueba sin esas variables en autostart.

## systemd --user

Si usas el servicio de ejemplo, asegúrate de tenerlo habilitado para tu usuario y de que el `ExecStart` apunte al script con ruta absoluta. Ver [`contrib/jarvis-user.service.example`](../contrib/jarvis-user.service.example).
