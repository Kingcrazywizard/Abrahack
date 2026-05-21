# Hyprland — Gestión de Wallpaper

## Script `setwall` · Persistente · Multi-monitor · Hacker Workflow

---

## Objetivo

Cambiar el wallpaper con un solo comando:

```bash
setwall cyberpunk.png
```

Con las siguientes garantías:

- Cambia instantáneamente
- Sobrevive reboot
- Sobrevive reload de Hyprland
- Funciona en multi-monitor
- Sin editar configs manualmente

---

## PASO 1 — Crear el Script Principal

```bash
mkdir -p ~/.local/bin
nano ~/.local/bin/setwall
```

Pega el siguiente contenido:

```bash
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
```

Guarda con `Ctrl+O` → `Enter` → `Ctrl+X`

---

## PASO 2 — Dar Permisos al Script

```bash
chmod +x ~/.local/bin/setwall
```

---

## PASO 3 — Añadir al PATH

```bash
nano ~/.zshrc
```

Agrega al final:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Aplica los cambios:

```bash
source ~/.zshrc
```

---

## PASO 4 — Crear Script de Restauración Automática

Este script restaura el último wallpaper usado al iniciar Hyprland:

```bash
nano ~/.local/bin/wallrestore
```

Pega el siguiente contenido:

```bash
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
```

Guarda con `Ctrl+O` → `Enter` → `Ctrl+X`

Permisos:

```bash
chmod +x ~/.local/bin/wallrestore
```

---

## PASO 5 — Configurar Autostart en Hyprland

```bash
nano ~/.config/hypr/hyprland.conf
```

**Elimina** esta línea si existe:

```ini
exec-once = hyprpaper
```

**Agrega** esta en su lugar:

```ini
exec-once = /home/kingwizard/.local/bin/wallrestore
```

---

## PASO 6 — Uso

Coloca tus wallpapers en:

```bash
~/Pictures/Wallpapers/
```

Cambia el wallpaper con:

```bash
setwall nombre-imagen.png
```

Al hacer reboot o reload, se restaura automáticamente el último wallpaper usado.

---

## Ventajas

|Característica|Estado|
|:--|:--|
|Persistente entre reinicios|✅|
|Limpio, sin configs rotas|✅|
|Modular y extensible|✅|
|Multi-monitor|✅|
|Hacker workflow|✅|
|Fácil de scripting|✅|

---

## Roadmap de Automatizaciones

Ideas para expandir este sistema en fases futuras:

```bash
setwall random          # wallpaper aleatorio de la carpeta
```

- Wallpapers rotativos por tiempo
- Wallpapers generados por IA
- Wallpapers dinámicos (video/animación)
- Wallpapers por workspace
- Wallpapers reactivos a métricas de CPU/GPU
- Cyberpunk animated setups
- Integración con OpenClaw para cambio por comando de voz o agente