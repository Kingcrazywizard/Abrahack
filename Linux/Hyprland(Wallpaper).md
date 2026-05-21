OBJETIVO editar

Que puedas cambiar wallpaper así:

setwall cyberpunk.png

y:

cambie instantáneamente
sobreviva reboot
sobreviva reload
multi monitor
sin editar configs manualmente

PASO 1 — Crear script profesional
mkdir -p ~/.local/bin
nano ~/.local/bin/setwall
Pega EXACTAMENTE esto
#!/bin/bash

WALL="$1"

if [ -z "$WALL" ]; then
    echo "Uso: setwall imagen.png"
    exit 1
fi

WALLPATH="$HOME/Pictures/Wallpapers/$WALL"

if [ ! -f "$WALLPATH" ]; then
    echo "No existe: $WALLPATH"
    exit 1
fi

pkill hyprpaper

hyprpaper >/dev/null 2>&1 &

sleep 1

hyprctl hyprpaper wallpaper "HDMI-A-1,$WALLPATH"
hyprctl hyprpaper wallpaper "DP-2,$WALLPATH"

echo "$WALLPATH" > ~/.cache/current_wallpaper

echo "Wallpaper aplicado: $WALL"
Guardar
CTRL + O
ENTER
CTRL + X
PASO 2 — Dar permisos
chmod +x ~/.local/bin/setwall
PASO 3 — Añadir al PATH

Abre:

nano ~/.zshrc
Agrega al final
export PATH="$HOME/.local/bin:$PATH"
Aplicar:
source ~/.zshrc
PASO 4 — Crear restauración automática

Ahora:

nano ~/.local/bin/wallrestore
Pega esto
#!/bin/bash

sleep 3

WALL=$(cat /home/kingwizard/.cache/current_wallpaper 2>/dev/null)

if [ -z "$WALL" ]; then
    exit 1
fi

pkill hyprpaper

hyprpaper >/dev/null 2>&1 &

sleep 2

hyprctl hyprpaper wallpaper "HDMI-A-1,$WALL"
hyprctl hyprpaper wallpaper "DP-2,$WALL"
Guardar
CTRL + O
ENTER
CTRL + X
Permisos
chmod +x ~/.local/bin/wallrestore
PASO 5 — Hyprland autostart LIMPIO

Abre:

nano ~/.config/hypr/hyprland.conf
ELIMINA:
exec-once = hyprpaper
Y agrega:
exec-once = /home/kingwizard/.local/bin/wallrestore

PASO 6 — Guardar permisos
chmod +x ~/.local/bin/wallrestore

PASO 7 — TEST MANUAL

SIN reboot todavía:
RESULTADO FINAL

Ahora:

cambiar wallpaper:
setwall wallpaper.png
reboot/login:

se restaura automáticamente.

VENTAJAS

✅ persistente
✅ limpio
✅ modular
✅ multi monitor
✅ hacker workflow
✅ sin configs rotas
✅ fácil scripting
✅ extensible

Más adelante podrás hacer:
setwall random

o:

wallpapers rotativos
wallpapers IA
wallpapers dinámicos
wallpapers por workspace
wallpapers reactivos a CPU/GPU
cyberpunk animated setups