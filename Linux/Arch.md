# Abrahack OS — Master Guide v2
## Arch Linux + Hyprland + Hacker Workflow

> **Estado del documento:** Revisado y expandido. Incluye correcciones críticas para NVIDIA + Wayland, miniguías de CLI, Bluetooth, Pipewire y gestión de workspaces funcional.

---

## Filosofía Abrahack

**Objetivo del sistema:**
- Sistema operativo minimalista y controlado al 100%
- Workflow orientado puramente al teclado (*keyboard-driven*)
- Infraestructura de IA local y agentes cognitivos
- Contenerización avanzada con Docker y Podman
- Integración nativa con OpenClaw y Claude para la creación de herramientas
- Desarrollo ofensivo y automatización avanzada
- Estética cyberpunk y hacker funcional

**Hardware objetivo:**

| Componente | Especificación |
| :--- | :--- |
| CPU | Intel i7-7700 |
| GPU | NVIDIA GTX 1060 6GB |
| Almacenamiento | NVMe SSD 1TB |
| RAM | 8GB DDR4 |

---

## PARTE 1 — Instalación de Arch Linux

### 1.1 Descarga del Sistema
- **ISO Oficial:** https://archlinux.org/download/

### 1.2 Creación del Medio de Arranque (Rufus en Windows)

| Campo | Valor |
| :--- | :--- |
| Partition Scheme | GPT |
| Target System | UEFI |
| Filesystem | Large FAT32 |
| Cluster Size | 32 KB |
| Persistent Partition | 0 |
| Image Mode | ISO |

> ⚠️ **No** usar modo DD ni seleccionar Legacy BIOS.

### 1.3 Configuración de la BIOS

Antes de arrancar desde el USB, verificar estos valores en la BIOS:

- **Desactivar:** Secure Boot, Fast Boot, CSM (Compatibility Support Module)
- **Activar:** UEFI Only, AHCI (modo SATA)

### 1.4 Verificación del Modo UEFI

Una vez cargado el entorno de la ISO:

```bash
ls /sys/firmware/efi
```

Si el comando devuelve carpetas y archivos, el arranque en modo UEFI es correcto. Si el directorio no existe, reinicia y revisa la BIOS.

### 1.5 Conexión a Internet

**Ethernet:** Se conecta automáticamente por DHCP.

**Wi-Fi:**
```bash
iwctl
# Dentro de iwctl:
[iwd]# device list
[iwd]# station wlan0 scan
[iwd]# station wlan0 connect "NombreDeRedWiFi"
[iwd]# quit

# Verificar conexión
ping -c 3 archlinux.org
```

### 1.6 Sincronizar Reloj del Sistema

```bash
timedatectl set-ntp true
timedatectl status
# Debe mostrar: NTP service: active
```

### 1.7 Lanzamiento del Instalador

```bash
archinstall
```

### 1.8 Configuración Recomendada en archinstall

Navega el menú con las flechas del teclado y `Enter`:

| Opción | Valor recomendado |
| :--- | :--- |
| Mirrors | Colombia o USA |
| Locale | es_CO.UTF-8 |
| Disk config | Best effort / BTRFS |
| Filesystem | BTRFS con compresión |
| Swap | zram (compresión: zstd) |
| Bootloader | systemd-boot |
| Hostname | abrahack-node |
| Kernel | linux |
| Desktop | **plasma-meta** (entorno de respaldo estable) |
| Greeter | SDDM |
| Graphics | **nouveau** (temporal, se reemplazará por drivers propietarios) |
| Audio | pipewire |
| Network | NetworkManager |

### 1.9 Paquetes Adicionales Iniciales

En el campo "Additional packages" de archinstall, pegar esto:

```
git base-devel wget curl unzip zip htop btop fastfetch tmux neovim python python-pip nodejs npm jdk-openjdk rust go openssh kitty zsh vlc
```

### 1.10 Finalización y Primer Arranque

1. Selecciona **Save Configuration → YES**
2. Configura usuario y contraseña (**Save User Credentials → YES**)
3. Encrypt Credentials: **NO**
4. Presiona **Install** y espera
5. Al terminar, reinicia y retira el USB
6. Haz login y actualiza el sistema:

```bash
sudo pacman -Syu
```

---

## PARTE 2 — El Talón de Aquiles: NVIDIA + Wayland ⚠️ (Debug pendiente)

> **Esta es la sección más crítica del setup.** Tu GTX 1060 requiere drivers propietarios para que Hyprland funcione sin congelamientos. El driver `nouveau` que instalaste es solo temporal.

### 2.1 Por qué nouveau no funciona con Hyprland

`nouveau` es el driver open-source de NVIDIA. Funciona para Plasma básico, pero **no implementa correctamente el protocolo GBM** que Wayland necesita. En tarjetas GTX 900/1000 series esto se traduce en:
- Pantalla negra al arrancar Hyprland
- Congelamientos aleatorios
- Animaciones rotas o ausentes

### 2.2 Instalación del Driver Propietario

```bash
# Desde Plasma (antes de entrar a Hyprland)
sudo pacman -S nvidia nvidia-utils lib32-nvidia-utils
```

### 2.3 Configurar los Parámetros del Kernel (systemd-boot)

> **Esta es la parte donde quedaste atascado.** Aquí está la explicación completa para no dañar nada.

**Primero, localiza tu archivo de configuración:**

```bash
# Listar todos los archivos de arranque disponibles
ls /boot/loader/entries/

# Si no encuentra nada ahí, buscar en toda la partición EFI
ls /efi/loader/entries/
# o
find /boot -name "*.conf" 2>/dev/null
find /efi -name "*.conf" 2>/dev/null
```

Verás un archivo con un nombre como `arch.conf` o `2024-01-01_linux.conf`. **Ese es tu archivo objetivo.**

**Editar el archivo encontrado:**

```bash
# Sustituye la ruta por la que encontraste arriba
sudo nano /boot/loader/entries/arch.conf
```

El archivo tiene una estructura así:

```
title   Arch Linux
linux   /vmlinuz-linux
initrd  /initramfs-linux.img
options root=UUID=xxxx-xxxx rw
```

**Modifica la línea `options` para que quede así:**

```
options root=UUID=xxxx-xxxx rw nvidia_drm.modeset=1 nvidia_drm.fbdev=1
```

> ⚠️ **No borres nada de lo que ya existe en esa línea.** Solo añade los dos parámetros al **final**, separados por un espacio. El UUID y el resto deben permanecer exactamente igual.

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Verificar que los módulos cargan al arranque:**

```bash
# Añadir módulos de nvidia al initramfs
sudo nano /etc/mkinitcpio.conf
```

Busca la línea `MODULES=()` y modifícala:

```
MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

Luego regenerar el initramfs:

```bash
sudo mkinitcpio -P
```

**Finalmente, reiniciar:**

```bash
reboot
```

---

## PARTE 3 — Configurar AUR (yay)

El AUR (Arch User Repository) contiene miles de paquetes que no están en los repositorios oficiales, incluyendo la mayoría de herramientas de IA.

```bash
cd /tmp
git clone https://aur.archlinux.org/yay-bin.git
cd yay-bin
makepkg -si
```

> **Uso:** A partir de ahora usa `yay -S nombre-paquete` para instalar desde el AUR. No necesitas `sudo`, yay lo pedirá solo cuando sea necesario.

---

## PARTE 4 — Audio con Pipewire

### 4.1 Qué es cada componente (y cuál necesitas realmente)

Instalaste varios paquetes de audio. Aquí está para qué sirve cada uno:

| Paquete | Para qué sirve | ¿Necesario? |
| :--- | :--- | :--- |
| `pipewire` | El servidor de audio central. Sin esto, no hay sonido. | ✅ Sí |
| `pipewire-pulse` | Compatibilidad con apps que usan PulseAudio (la mayoría). | ✅ Sí |
| `pipewire-alsa` | Compatibilidad con apps que usan ALSA (terminales, juegos viejos). | ✅ Sí |
| `wireplumber` | El gestor de sesiones. Decide qué audio va a dónde. Sin esto, Pipewire arranca pero no hace nada. | ✅ Sí |
| `pavucontrol` | Interfaz gráfica para controlar volumen, salidas y entradas. Igual al mezclador de Windows. | ⚙️ Opcional pero muy útil |

**En resumen:** Los cuatro primeros son el motor. `pavucontrol` es el panel de control visual.

### 4.2 Activar Pipewire

```bash
# Habilitar todos los servicios de audio para tu usuario
systemctl --user enable --now pipewire pipewire-pulse wireplumber

# Verificar que está corriendo
systemctl --user status pipewire
```

### 4.3 Si no hay sonido

```bash
# Ver qué dispositivo de audio detectó Pipewire
pactl list sinks short

# Ver el estado completo
wpctl status

# Abrir el mezclador gráfico
pavucontrol
```

---

## PARTE 5 — Bluetooth con bluetoothctl

`bluetoothctl` es el comando para gestionar Bluetooth desde terminal. Aquí la guía de uso.

### 5.1 Instalación y activación

```bash
sudo pacman -S bluez bluez-utils
sudo systemctl enable --now bluetooth
```

### 5.2 Cómo usar bluetoothctl paso a paso

```bash
# Entrar al intérprete de Bluetooth
bluetoothctl
```

Una vez dentro, el prompt cambia a `[bluetooth]#`. Estos son los comandos:

```bash
# Encender el adaptador Bluetooth
power on

# Poner el adaptador en modo descubrimiento (buscar dispositivos)
scan on

# Esperar unos segundos. Verás dispositivos aparecer así:
# [NEW] Device AA:BB:CC:DD:EE:FF Mi Auricular

# Emparejar con el dispositivo (reemplaza la MAC por la que viste)
pair AA:BB:CC:DD:EE:FF

# Si pide confirmación, escribe: yes

# Conectar al dispositivo
connect AA:BB:CC:DD:EE:FF

# Marcar como dispositivo de confianza (auto-conecta en el futuro)
trust AA:BB:CC:DD:EE:FF

# Detener el escaneo
scan off

# Salir de bluetoothctl
exit
```

### 5.3 Comandos útiles adicionales

```bash
# Ver dispositivos emparejados
paired-devices

# Ver dispositivos conectados ahora mismo
devices Connected

# Desconectar un dispositivo
disconnect AA:BB:CC:DD:EE:FF

# Ver información de un dispositivo
info AA:BB:CC:DD:EE:FF
```

---

## PARTE 6 — Instalación de Hyprland

### 6.1 Componentes de la Interfaz

```bash
sudo pacman -S hyprland waybar kitty rofi-wayland hyprpaper dunst \
  dolphin xdg-desktop-portal-hyprland xdg-desktop-portal-gtk \
  qt5-wayland qt6-wayland polkit-kde-agent grim slurp wl-clipboard \
  zsh starship
```

> ⚠️ Nota: el paquete correcto es `grim`, no `grimm` (typo en la guía anterior).

### 6.2 Gestor de Autenticación Gráfico

**Evaluación de la sugerencia de Gemini (`lxsession`):**

`lxsession` es un polkit agent de GTK2, una tecnología de 2009. Funciona, pero es inconsistente con el stack moderno (Wayland + Qt). Para Abrahack, la mejor opción es `polkit-kde-agent` (ya instalado arriba), que es nativo de KDE/Plasma y se integra perfectamente con Hyprland.

**No instales `lxsession`.** En su lugar, usa:

```bash
# Ya instalado: polkit-kde-agent
# Asegúrate de tenerlo en el autostart de Hyprland (ver sección 6.4)
```

### 6.3 Crear el Directorio de Configuración

```bash
mkdir -p ~/.config/hypr
nano ~/.config/hypr/hyprland.conf
```

### 6.4 Configuración Base Completa (hyprland.conf)

```ini
 # --- Monitor ---
   2 │ # Formato: monitor=nombre,resolución,posición,escala
   3 │ monitor=,preferred,auto,1
   4 │
   5 │ # --- Input ---
   6 │ input {
   7 │     kb_layout = us
   8 │     follow_mouse = 1
   9 │     touchpad {
  10 │         natural_scroll = no
  11 │     }
  12 │ }
  13 │
  14 │ # --- Apariencia general ---
  15 │ general {
  16 │     gaps_in = 5
  17 │     gaps_out = 10
  18 │     border_size = 2
  19 │     col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
  20 │     col.inactive_border = rgba(595959aa)
  21 │     layout = dwindle
  22 │ }
  23 │
  24 │ # --- Autostart ---
  25 │ exec-once = waybar
  26 │ exec-once = dunst
  27 │ exec-once = hyprpaper
  28 │ exec-once = /usr/lib/polkit-kde-authentication-agent-1
  29 │
  30 │ # =========================================================
     │ ===
  31 │ #  ATAJOS DE TECLADO
  32 │ # =========================================================
     │ ===
  33 │
  34 │ $mainMod = SUPER
  35 │
  36 │ # Aplicaciones principales
  37 │ bind = $mainMod, RETURN, exec, kitty
  38 │ bind = $mainMod, D, exec, rofi -show drun
  39 │ bind = $mainMod, Q, killactive
  40 │ bind = $mainMod, F, fullscreen
  41 │ bind = $mainMod, V, togglefloating
  42 │ bind = $mainMod, P, pseudo
  43 │
  44 │
  45 │ # Movimiento de foco entre ventanas
  46 │ bind = $mainMod, left, movefocus, l
  47 │ bind = $mainMod, right, movefocus, r
  48 │ bind = $mainMod, up, movefocus, u
  49 │ bind = $mainMod, down, movefocus, d
  50 │
  51 │ # Mover ventanas dentro del tiling
  52 │ bind = $mainMod SHIFT, left, movewindow, l
  53 │ bind = $mainMod SHIFT, right, movewindow, r
  54 │ bind = $mainMod SHIFT, up, movewindow, u
  55 │ bind = $mainMod SHIFT, down, movewindow, d
  56 │
  57 │ # Redimensionar ventanas (modo resize)
  58 │ bind = $mainMod, R, submap, resize
  59 │ submap = resize
  60 │ binde = , right, resizeactive, 30 0
  61 │ binde = , left, resizeactive, -30 0
  62 │ binde = , up, resizeactive, 0 -30
  63 │ binde = , down, resizeactive, 0 30
  64 │ bind = , escape, submap, reset
  65 │ submap = reset
  66 │
  67 │ # =========================================================
     │ ===
  68 │ #  WORKSPACES — CAMBIO Y MOVIMIENTO (CORRECCIÓN)
  69 │ # =========================================================
     │ ===
  70 │ # El problema anterior: las teclas numéricas pueden necesit
     │ ar
  71 │ # el nombre exacto según tu layout de teclado.
  72 │ # Esta sintaxis es la más compatible:
  73 │
  74 │ bind = $mainMod, 1, workspace, 1
  75 │ bind = $mainMod, 2, workspace, 2
  76 │ bind = $mainMod, 3, workspace, 3
  77 │ bind = $mainMod, 4, workspace, 4
  78 │ bind = $mainMod, 5, workspace, 5
  79 │ bind = $mainMod, 6, workspace, 6
  80 │ bind = $mainMod, 7, workspace, 7
  81 │ bind = $mainMod, 8, workspace, 8
  82 │ bind = $mainMod, 9, workspace, 9
  83 │ bind = $mainMod, 0, workspace, 10
  84 │
  85 │ # Mover ventana activa a workspace
  86 │ bind = $mainMod SHIFT, 1, movetoworkspace, 1
  87 │ bind = $mainMod SHIFT, 2, movetoworkspace, 2
  88 │ bind = $mainMod SHIFT, 3, movetoworkspace, 3
  89 │ bind = $mainMod SHIFT, 4, movetoworkspace, 4
  90 │ bind = $mainMod SHIFT, 5, movetoworkspace, 5
  91 │ bind = $mainMod SHIFT, 6, movetoworkspace, 6
  92 │ bind = $mainMod SHIFT, 7, movetoworkspace, 7
  93 │ bind = $mainMod SHIFT, 8, movetoworkspace, 8
  94 │ bind = $mainMod SHIFT, 9, movetoworkspace, 9
  95 │ bind = $mainMod SHIFT, 0, movetoworkspace, 10
  96 │
  97 │ # Scroll sobre la barra para cambiar workspace
  98 │ bind = $mainMod, mouse_down, workspace, e+1
  99 │ bind = $mainMod, mouse_up, workspace, e-1
 100 │
 101 │ # Mover/redimensionar ventanas con mouse
 102 │ bindm = $mainMod, mouse:272, movewindow
 103 │ bindm = $mainMod, mouse:273, resizewindow
 104 │
 105 │ # Screenshots
 106 │ bind = , Print, exec, grim ~/Pictures/screenshot-$(date +%F
     │ -%T).png
 107 │ bind = SHIFT, Print, exec, grim -g "$(slurp)" ~/Pictures/sc
     │ reenshot-$(date +%F-%T).png
```

> **Diagnóstico del problema de workspaces:** Si los keybinds de números no funcionan, el problema más común es un conflicto con el layout de teclado. Si tienes `kb_layout = latam` o `es`, las teclas numéricas tienen nombres distintos internamente. Con `kb_layout = us` los binds de arriba funcionan sin modificación.

### 6.5 Solucionar Workspace que No Responde

Si después de aplicar la config los workspaces aún no cambian, ejecuta esto para diagnosticar:

```bash
# Ver qué nombre le da Hyprland a las teclas que presionas
wev
# Presiona las teclas numéricas y observa el campo "sym"
# El valor que ves ahí es el que debes usar en el bind
```

Instala `wev` con:
```bash
sudo pacman -S wev
```

---

## PARTE 7 — Cambio de Tipografía y Paleta de Colores

### 7.1 Tipografía: JetBrains Mono Nerd Font

```bash
sudo pacman -S ttf-jetbrains-mono-nerd noto-fonts-emoji
fc-cache -fv
```

**Aplicar en Kitty** (`~/.config/kitty/kitty.conf`):

```ini
font_family      JetBrainsMono Nerd Font Mono
bold_font        JetBrainsMono Nerd Font Mono Bold
italic_font      JetBrainsMono Nerd Font Mono Italic
font_size        12.0
```

**Verificar que la fuente fue detectada:**

```bash
fc-list | grep -i jetbrains
# Debe devolver resultados con la ruta de la fuente
```

### 7.2 Paletas de Colores para Kitty

Arch Linux usa Kitty como terminal. Las paletas se aplican directamente en `~/.config/kitty/kitty.conf`.

**Opción A — Tokyo Night (recomendada para estética hacker):**

```ini
# Tokyo Night
foreground              #c0caf5
background              #1a1b26
selection_foreground    #c0caf5
selection_background    #283457
color0                  #15161e
color1                  #f7768e
color2                  #9ece6a
color3                  #e0af68
color4                  #7aa2f7
color5                  #bb9af7
color6                  #7dcfff
color7                  #a9b1d6
color8                  #414868
color9                  #f7768e
color10                 #9ece6a
color11                 #e0af68
color12                 #7aa2f7
color13                 #bb9af7
color14                 #7dcfff
color15                 #c0caf5
```

**Opción B — Catppuccin Mocha:**

```ini
# Catppuccin Mocha
foreground              #cdd6f4
background              #1e1e2e
selection_foreground    #1e1e2e
selection_background    #f5c2e7
color0                  #45475a
color1                  #f38ba8
color2                  #a6e3a1
color3                  #f9e2af
color4                  #89b4fa
color5                  #f5c2e7
color6                  #94e2d5
color7                  #bac2de
color8                  #585b70
color9                  #f38ba8
color10                 #a6e3a1
color11                 #f9e2af
color12                 #89b4fa
color13                 #f5c2e7
color14                 #94e2d5
color15                 #a6adc8
```

### 7.3 Gestión de Transparencias

Las transparencias **no se configuran en un solo lugar**, cada componente tiene su propio control:

| Componente | Dónde configurar | Parámetro |
| :--- | :--- | :--- |
| Kitty | `~/.config/kitty/kitty.conf` | `background_opacity 0.90` |
| Waybar | `~/.config/waybar/style.css` | `background-color: rgba(26,27,38,0.85)` |
| Rofi | `~/.config/rofi/config.rasi` | `background-color: rgba(26, 27, 38, 0.9);` |
| Hyprland (blur) | `hyprland.conf` sección `decoration` | `blur { enabled = true; size = 3; }` |

**Kitty completo con transparencia:**

```ini
background_opacity 0.90
dynamic_background_opacity yes
# Cambiar opacidad con: Ctrl+Shift+A (más) / Ctrl+Shift+B (menos)
```

---

## PARTE 8 — Inicialización de Hyprland

Cierra sesión de Plasma. En la pantalla de SDDM, busca el selector de sesión (esquina inferior izquierda o inferior derecha según tu tema) y cambia de **Plasma** a **Hyprland**. Ingresa tus credenciales.

**Para arranque automático desde TTY (más limpio):**

Agrega al final de `~/.bash_profile` o `~/.zprofile`:

```bash
if [ -z "$DISPLAY" ] && [ "$XDG_VTNR" = 1 ]; then
    exec Hyprland
fi
```

---

## PARTE 9 — Docker

### 9.1 Activación del Demonio

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# OBLIGATORIO: reiniciar para que el grupo surta efecto
reboot
```

### 9.2 Solución al Error `docker.sock`

Si aparece `failed to connect to docker.sock`:

```bash
# Limpiar configuración residual de Docker Desktop
rm -rf ~/.docker

# Verificar que el socket existe
ls -la /var/run/docker.sock
```

### 9.3 Verificación

```bash
docker ps
docker run hello-world
```

---

## PARTE 10 — Flujo de Trabajo en Hyprland

### Distribución de Workspaces (Abrahack Workflow)

| Workspace | Uso |
| :--- | :--- |
| 1 | Terminal principal (Kitty) |
| 2 | Navegador web e investigación |
| 3 | IDE / Editor de código (VSCode / Neovim) |
| 4 | Monitoreo e infraestructura (Docker, logs, btop) |
| 5 | Orquestación de IA (Claude, OpenClaw, Ollama) |

### Referencia de Atajos Completa

| Atajo | Acción |
| :--- | :--- |
| `SUPER + ENTER` | Abre Kitty |
| `SUPER + D` | Lanza Rofi (buscador de apps) |
| `SUPER + Q` | Cierra ventana activa |
| `SUPER + F` | Pantalla completa |
| `SUPER + V` | Alternar flotante/tiling |
| `SUPER + R` | Modo redimensionar (usa flechas, ESC para salir) |
| `SUPER + Flechas` | Mover foco entre ventanas |
| `SUPER + SHIFT + Flechas` | Mover ventana en el tiling |
| `SUPER + 1-9` | Cambiar al workspace N |
| `SUPER + SHIFT + 1-9` | Mover ventana al workspace N |
| `SUPER + Mouse Izquierdo` | Arrastrar ventana flotante |
| `SUPER + Mouse Derecho` | Redimensionar ventana |
| `Print` | Screenshot de pantalla completa |
| `SHIFT + Print` | Screenshot de área seleccionada |

---

## PARTE 11 — Configuración de Kitty Terminal

```bash
mkdir -p ~/.config/kitty
nano ~/.config/kitty/kitty.conf
```

Configuración base:

```ini
# Fuente
font_family      JetBrainsMono Nerd Font Mono
font_size        12.0

# Apariencia
background_opacity 0.90
cursor_shape beam
cursor_blink_interval 0.5

# Comportamiento
enable_audio_bell no
visual_bell_duration 0.0
confirm_os_window_close 0

# Copiar/pegar
copy_on_select yes
strip_trailing_spaces smart
```

---

## PARTE 12 — Shell: ZSH + Starship

```bash
# Cambiar shell por defecto
chsh -s /bin/zsh

# Instalar Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Activar Starship en ZSH (agregar al final de ~/.zshrc)
echo 'eval "$(starship init zsh)"' >> ~/.zshrc

# Recargar configuración
source ~/.zshrc
```

---

## PARTE 13 — Estética Cyberpunk

### 13.1 Paquetes Visuales

```bash
# Visualizadores y herramientas de terminal
sudo pacman -S cmatrix neofetch fastfetch btop

# Iluminación RGB
sudo pacman -S openrgb
```

### 13.2 Comunidades y Dotfiles de Inspiración

> ⚠️ **Regla de oro:** No clones ni ejecutes scripts de dotfiles completos sin leer cada línea. El aprendizaje real en Arch Linux se destruye con instaladores automáticos de terceros.

- **r/hyprland** y **r/unixporn** en Reddit
- ML4W Dotfiles
- End-4 Dots
- HyDE Project
- JaKooLit Dots

---

## PARTE 14 — Entorno de Desarrollo

### 14.1 VS Code con Soporte Wayland Nativo

```bash
sudo pacman -S code

# Crear alias con flags Wayland en ~/.zshrc
echo "alias code='code --enable-features=UseOzonePlatform --ozone-platform=wayland'" >> ~/.zshrc
source ~/.zshrc
```

### 14.2 Python + uv (Gestor Moderno)

```bash
# Instalar uv (reemplaza pip + virtualenv, escrito en Rust, 100x más rápido)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno virtual para Abrahack
uv venv ~/.venvs/abrahack
source ~/.venvs/abrahack/bin/activate

# Paquetes base de IA
uv pip install anthropic httpx rich typer
```

### 14.3 Git

```bash
git config --global user.name "Abrahack Lab"
git config --global user.email "tu@email.com"
git config --global core.editor nvim

# SSH key para GitHub
ssh-keygen -t ed25519 -C "abrahack@arch"
cat ~/.ssh/id_ed25519.pub
# Copiar el output y pegarlo en GitHub → Settings → SSH Keys
```

---

## PARTE 15 — Miniguías de CLI Modernas

Estas herramientas reemplazan los comandos Unix tradicionales con alternativas más rápidas y visuales.

### 15.1 Instalación

```bash
sudo pacman -S eza bat ripgrep fd fzf zoxide lazygit btop fastfetch
```

### 15.2 eza — reemplaza `ls`

```bash
# Listado con iconos y colores
eza --icons

# Ver árbol de directorios
eza --tree --level=2 --icons

# Ver con permisos y tamaños legibles
eza -lh --icons

# Alias recomendados (añadir a ~/.zshrc):
alias ls='eza --icons'
alias ll='eza -lh --icons'
alias lt='eza --tree --level=2 --icons'
```

### 15.3 bat — reemplaza `cat`

```bash
# Ver archivo con syntax highlighting
bat archivo.py

# Ver con número de líneas
bat -n archivo.py

# Ver sin decoración (útil para pipes)
bat --plain archivo.txt

# Alias recomendado:
alias cat='bat'
```

### 15.4 ripgrep (rg) — reemplaza `grep`

```bash
# Buscar texto en todos los archivos del directorio actual
rg "función_que_busco"

# Buscar solo en archivos Python
rg "def main" --type py

# Buscar ignorando mayúsculas
rg -i "api_key"

# Ver contexto alrededor del resultado
rg "error" -C 3

# Alias recomendado:
alias grep='rg'
```

### 15.5 fd — reemplaza `find`

```bash
# Buscar archivo por nombre
fd nombre_archivo

# Buscar solo archivos Python
fd --extension py

# Buscar en directorio específico
fd config ~/.config

# Buscar y ejecutar comando sobre resultado
fd --extension md --exec bat {}
```

### 15.6 fzf — búsqueda fuzzy interactiva

```bash
# Búsqueda interactiva en historial de comandos
Ctrl+R   # (fzf lo intercepta automáticamente en zsh)

# Seleccionar archivo interactivamente
vim $(fzf)

# Buscar y abrir con bat
fzf --preview 'bat --color=always {}'

# Buscar proceso para matar
kill -9 $(ps aux | fzf | awk '{print $2}')
```

### 15.7 zoxide — reemplaza `cd`

```bash
# Primera vez: inicializar en ~/.zshrc
echo 'eval "$(zoxide init zsh)"' >> ~/.zshrc
source ~/.zshrc

# Uso: ir a cualquier directorio visitado antes con solo escribir parte del nombre
z workspace       # va a ~/Workspace/
z docker          # va a ~/Workspace/Docker/
z abr             # va a cualquier directorio que contenga "abr"

# Ver historial de directorios
zoxide query --list
```

### 15.8 lazygit — Git visual en terminal

```bash
# Abrir en el repositorio actual
lazygit

# Navegación dentro de lazygit:
# h/j/k/l o flechas = moverse
# espacio = staging de archivo
# c = commit
# p = push
# P = pull
# q = salir
```

### 15.9 btop — monitor de sistema

```bash
btop

# Dentro de btop:
# m = cambiar vista de memoria
# n = vista de red
# d = vista de disco
# q = salir
# F2 = opciones
```

---

## PARTE 16 — Estructura Jerárquica del Workspace

```bash
# Crear la estructura completa de directorios
mkdir -p ~/Workspace/{Agents,OpenClaw,Juriscope,Docker,Models,Scripts}

# Verificar
eza --tree ~/Workspace --icons
```

Resultado esperado:

```
~/Workspace/
├── Agents/       # Scripts autónomos desarrollados con Claude
├── OpenClaw/     # Repositorio y herramientas de OpenClaw
├── Juriscope/    # Proyectos específicos y automatizaciones
├── Docker/       # Archivos docker-compose e infraestructura
├── Models/       # Modelos LLM e IA locales (Ollama)
└── Scripts/      # Utilidades y automatizaciones del sistema
```

---

## PARTE 17 — Roadmap de Infraestructura Abrahack

```
FASE 1: Interfaz y Core   ✅  Hyprland + Kitty + Docker + VSCode + Git
FASE 2: IA Local Base     →   Ollama + modelos locales + API Anthropic
FASE 3: Automatización    →   Agentes con Claude + OpenClaw + scripts de terminal
FASE 4: Especialización   →   Juriscope + herramientas ofensivas + workflows avanzados
```

---

## Apéndice — Diagnóstico Rápido

```bash
# Ver logs de Hyprland en tiempo real
journalctl -f --user -u hyprland

# Ver qué nombre tienen las teclas en tu layout
wev

# Verificar que NVIDIA cargó correctamente
nvidia-smi
lsmod | grep nvidia

# Ver resolución y monitores activos
hyprctl monitors

# Recargar config de Hyprland sin reiniciar
hyprctl reload

# Estado de todos los servicios de usuario
systemctl --user status
```

---

*Documento generado para Abrahack Lab · Arch Linux + Hyprland · GTX 1060*