Activación de Servicios de Audio

Los servicios de PipeWire corren en el espacio de usuario (sin sudo):
Bash

systemctl --user enable --now pipewire.service wireplumber.service pipewire-pulse.service

Para verificar que el backend esté respondiendo correctamente:
Bash

pactl info

Debe indicar en las últimas líneas: Nombre del servidor: PulseAudio (on PipeWire 1.x.x).
2. Configuración del Panel (~/.config/waybar/config)

Este archivo JSON unifica el módulo mpris para Spotify (usando Nerd Fonts), corrige las declaraciones de espacios de trabajo persistentes y añade interactividad con clics (on-click) para mezclar audio y redes.
JSON

{
  "layer": "top",
  "position": "top",
  "height": 36,
  "spacing": 8,
  "modules-left": [
    "custom/amun",
    "hyprland/workspaces"
  ],
  "modules-center": [
    "mpris",
    "clock"
  ],
  "modules-right": [
    "pulseaudio",
    "network",
    "tray"
  ],
  "custom/amun": {
    "format": " 𓂀 ",
    "tooltip": false
  },
  "hyprland/workspaces": {
    "format": "{icon}",
    "format-icons": {
      "1": "",
      "2": "",
      "3": "",
      "4": "",
      "5": "󰙯",
      "6": "",
      "active": "✦",
      "default": "·"
    },
    "persistent-workspaces": {
      "1": [],
      "2": [],
      "3": [],
      "4": [],
      "5": [],
      "6": []
    }
  },
  "mpris": {
    "format": " {player_icon} {dynamic} ",
    "format-paused": "  <i>{dynamic}</i> ",
    "player-icons": {
      "default": "",
      "spotify": ""
    },
    "max-length": 40
  },
  "clock": {
    "format": " {:%H:%M  %d %b} ",
    "tooltip": false
  },
  "pulseaudio": {
    "format": "{icon}  {volume}%",
    "format-muted": "󰝟  Muted",
    "format-icons": {
      "default": [
        "󰕿",
        "󰖀",
        "󰕾"
      ]
    },
    "on-click": "pavucontrol"
  },
  "network": {
    "format-wifi": "󰤨  {essid}",
    "format-ethernet": "󰈀  Wired",
    "format-disconnected": "󰤭  Offline",
    "tooltip-format": "{ifname} via {gwaddr}",
    "on-click": "nm-connection-editor"
  },
  "tray": {
    "spacing": 10
  }
}

3. Reglas de Ventana de Hyprland (~/.config/hypr/themes/amun/rules.conf)

Reglas estrictas con sintaxis limpia para confinar a Spotify al espacio de trabajo musical dedicado (6) y aplicar un difuminado estético transparente del 90%.
Plaintext

# Confinamiento del reproductor musical
windowrule {
  name = spotify-workspace
  match:class = spotify
  workspace = 6
}

windowrule {
  name = spotify-opacity
  match:class = spotify
  opacity = 0.90 0.80
}

4. Atajos de Teclado e Interactividad (~/.config/hypr/hyprland.conf)

Mapeo de teclas multimedia para control nativo de PipeWire (wpctl) y control multimedia de reproducción (playerctl). Incluye binds alternativos rápidos usando la tecla SUPER.
Plaintext

# ==========================================================
# AMUN-HACKER: CONTROL DE AUDIO Y MULTIMEDIA
# ==========================================================

# Control de Volumen del Sistema (PipeWire nativo)
bindel = , XF86AudioRaiseVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
bindel = , XF86AudioLowerVolume, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bindl  = , XF86AudioMute, exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle

# Control de Spotify / Medios con Playerctl
bindl = , XF86AudioPlay, exec, playerctl play-pause
bindl = , XF86AudioNext, exec, playerctl next
bindl = , XF86AudioPrev, exec, playerctl previous

# Atajos alternativos (Por si el teclado no tiene teclas multimedia físicas)
bind = SUPER, M, exec, spotify
bindel = SUPER, Up, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+
bindel = SUPER, Down, exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bindl = SUPER, Right, exec, playerctl next
bindl = SUPER, Left, exec, playerctl previous
bindl = SUPER, space, exec, playerctl play-pause

# Cambiar salida de audio entre TV (HDMI) y PC (Speakers/Audífonos)
bind = SUPER SHIFT, A, exec, ~/.config/hypr/scripts/toggle_audio.sh

5. Script Conmutador de Salidas de Audio (~/.config/hypr/scripts/toggle_audio.sh)

Script automatizado en Bash que lee el mapa actual de PipeWire e intercambia dinámicamente el flujo entre tu monitor principal/TV (HDMI - ID 51) y la salida física de la PC (ID 52), enviando una notificación nativa del sistema.
Bash

#!/bin/bash

# Obtener el ID del sumidero (sink) por defecto actual
CURRENT_SINK=$(wpctl status | grep -E '^\\s*\\*.*Sinks:' -A 5 | grep '*' | awk '{print $3}' | tr -d '.')

# IDs mapeados según el hardware del sistema
TV_SINK="51"
PC_SINK="52"

# Lógica de alternancia
if [ "$CURRENT_SINK" = "$TV_SINK" ]; then
    wpctl set-default $PC_SINK
    notify-send "Audio" "Cambiado a Altavoces/Audífonos de PC" --icon=audio-speakers
else
    wpctl set-default $TV_SINK
    notify-send "Audio" "Cambiado a Pantalla / LG TV" --icon=audio-card
fi

Asignación de Permisos de Ejecución:

No olvides otorgar permisos de ejecución al script tras crearlo:
Bash

chmod +x ~/.config/hypr/scripts/toggle_audio.sh

🚀 Secuencia de Recarga Completa

Para aplicar cualquier cambio futuro en la interfaz sin reiniciar el sistema, ejecuta la siguiente secuencia en tu terminal:
Bash

hyprctl reload && killall waybar && waybar & disown