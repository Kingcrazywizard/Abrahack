# ABRAHACK LAB — GUÍA DE INSTALACIÓN OPENCLAW
### Arch Linux + Hyprland + Podman + Ollama local

**Hardware:** Intel i7-7700 · GTX 1060 6GB · 8GB DDR4 · NVMe SSD  
**Stack:** Arch Linux · Hyprland Wayland · nvidia-580xx-dkms · Ollama · Podman rootless

---

## ARQUITECTURA

```
Host Arch Linux
├── Ollama (servicio systemd del sistema)
│   └── qwen2.5:7b-instruct-q4_K_M (GPU: GTX 1060 6GB)
│   └── qwen2.5-coder:7b (opcional, para tareas de código)
└── Podman rootless
    └── Contenedor abrahack/openclaw-configured
        └── OpenClaw Gateway (puerto 18789)
            └── Conecta a Ollama via 192.168.x.x:11434
```

**Decisiones arquitectónicas:**
- Ollama corre nativo — acceso directo a GPU sin overhead de contenedor
- OpenClaw contenido en Podman rootless — aislamiento del agente del sistema base
- Sin volúmenes — la config persiste via `podman commit` (evita conflictos de UID con VFS)
- Ollama escucha en `0.0.0.0` — accesible desde la red slirp4netns del contenedor

---

## FASE 1 — PREREQUISITOS DEL HOST

### Node.js via nvm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
source ~/.zshrc
nvm install 24
nvm use 24
nvm alias default 24
node -v   # v24.x.x
```

### pnpm

```bash
sudo pacman -S pnpm
```

### Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama --no-pager | head -3
```

### Modelos

```bash
# Modelo principal del agente (tool calling, instrucciones)
ollama pull qwen2.5:7b-instruct-q4_K_M

# Modelo de código (opcional)
ollama pull qwen2.5-coder:7b

# Verificar
ollama list
```

### Alias del modelo

```bash
echo 'alias archie="ollama run qwen2.5:7b-instruct-q4_K_M"' >> ~/.zshrc
source ~/.zshrc
```

### Exponer Ollama a la red del contenedor

Por defecto Ollama escucha solo en `127.0.0.1`. El contenedor Podman no puede
alcanzar esa dirección — hay que exponerlo en todas las interfaces:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d

sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama

# Verificar que escucha en todas las interfaces
ss -tlnp | grep 11434
# Debe mostrar: *:11434
```

---

## FASE 2 — PODMAN ROOTLESS

### Instalar Podman

```bash
sudo pacman -S podman podman-compose slirp4netns fuse-overlayfs
```

### Verificar subuid/subgid

```bash
cat /etc/subuid   # debe tener: tuusuario:100000:65536
cat /etc/subgid
```

Si no existen, agregarlos:

```bash
echo "$(whoami):100000:65536" | sudo tee -a /etc/subuid
echo "$(whoami):100000:65536" | sudo tee -a /etc/subgid
```

### Configurar storage VFS

VFS evita problemas de compatibilidad con el filesystem del host:

```bash
mkdir -p ~/.config/containers

cat > ~/.config/containers/storage.conf << 'EOF'
[storage]
driver = "vfs"
EOF
```

### Configurar contenedor hardened

```bash
cat > ~/.config/containers/containers.conf << 'EOF'
[containers]
pids_limit=256
netns="private"
ipcns="private"
utsns="private"
cgroupns="private"
userns="auto"
log_driver="k8s-file"
no_hosts=true
default_capabilities=[]

[engine]
cgroup_manager="cgroupfs"
events_logger="file"
EOF
```

### Verificar modo rootless

```bash
podman info | grep -i rootless
# Debe mostrar: rootless: true
```

### Limpiar storage previo (si existe)

```bash
rm -rf ~/.local/share/containers/storage
```

---

## FASE 3 — IMAGEN OPENCLAW

### Dockerfile

```bash
mkdir -p ~/abrahack-agent

cat > ~/abrahack-agent/Dockerfile << 'EOF'
FROM node:24-alpine

RUN apk add --no-cache curl git bash bluez --no-scripts

WORKDIR /root

RUN npm install -g pnpm openclaw@latest && \
    pnpm approve-builds -g 2>/dev/null || true

EXPOSE 18789
EOF
```

**Notas del Dockerfile:**
- Alpine en lugar de Debian — evita el problema del sandbox APT con Podman rootless
- `--no-scripts` — evita scripts de post-instalación que requieren `chown` privilegiado
- OpenClaw se instala como root — queda en `/usr/local/bin` y es accesible globalmente
- Sin usuario dedicado — root virtual dentro del contenedor, aislado por namespaces de Podman

### Build

```bash
podman build --userns=host -t abrahack/openclaw-agent ~/abrahack-agent/
```

`--userns=host` es necesario solo durante el build para que apk pueda escribir correctamente.

---

## FASE 4 — ONBOARDING

### Obtener IP del host

El contenedor usa `slirp4netns` — necesita la IP de la interfaz de red del host,
no `127.0.0.1`. Obtenerla con:

```bash
ip addr | grep inet | grep -v "127\|::1"
# Buscar la IP de la interfaz principal, ej: 192.168.18.2
```

### Lanzar contenedor para onboarding

```bash
podman run -it \
  --name openclaw-agent \
  --memory=2g \
  --cpus=3.0 \
  --pids-limit=256 \
  --cap-drop=ALL \
  --network=slirp4netns \
  --security-opt=no-new-privileges \
  -e OLLAMA_API_KEY="ollama-local" \
  abrahack/openclaw-agent \
  bash
```

**Asignación de recursos:**

| Recurso | Asignado al contenedor | Razón |
|---|---|---|
| RAM | 2GB | Ollama usa ~4.5GB, sistema ~1.5GB |
| CPUs | 3.0 cores | i7-7700 tiene 4 cores |
| PIDs | 256 | Previene fork bombs |
| Capabilities | DROP ALL | Sin acceso a capacidades kernel |

### Verificar antes de onboardear

```bash
# Dentro del contenedor
whoami                                    # root
openclaw --version                        # OpenClaw 2026.x.x
curl http://192.168.18.2:11434/api/tags  # debe devolver JSON con modelos
```

### Ejecutar onboarding

```bash
openclaw onboard --install-daemon
```

**Respuestas durante el wizard:**

| Pregunta | Respuesta |
|---|---|
| Security disclaimer | Yes |
| Setup mode | QuickStart |
| Model/auth provider | Ollama |
| Ollama mode | Local only |
| Ollama base URL | `http://192.168.18.2:11434` (tu IP) |
| Model | `qwen2.5:7b-instruct-q4_K_M` |
| Hatch agent | Hatch in Terminal |

### Verificar que el agente responde

En la TUI prueba:

```
hola
```

Debe responder en texto. Si la barra inferior muestra:
```
agent main | session main | ollama/qwen2.5:7b-instruct-q4_K_M | tokens x/33k
```
El stack está funcionando correctamente.

---

## FASE 5 — PERSISTENCIA VIA COMMIT

Al no usar volúmenes (por incompatibilidad de UIDs con VFS), la persistencia
se maneja guardando el estado del contenedor en la imagen:

```bash
# Salir de la TUI con Ctrl+C o Ctrl+D, luego desde el host:
podman commit openclaw-agent abrahack/openclaw-configured
```

**Importante:** hacer commit después de cualquier cambio de configuración
significativo — nuevas skills, cambios en openclaw.json, etc.

---

## FASE 6 — ALIASES DE ACCESO RÁPIDO

```bash
cat >> ~/.zshrc << 'EOF'

# Abrahack Lab — OpenClaw
alias abrahack='podman start openclaw-agent 2>/dev/null; podman exec -it openclaw-agent bash -c "openclaw tui"'
alias abrahack-shell='podman start openclaw-agent 2>/dev/null; podman exec -it openclaw-agent bash'
alias abrahack-save='podman commit openclaw-agent abrahack/openclaw-configured && echo "Estado guardado"'
EOF

source ~/.zshrc
```

| Alias | Función |
|---|---|
| `abrahack` | Abre la TUI del agente directamente |
| `abrahack-shell` | Bash dentro del contenedor para config |
| `abrahack-save` | Guarda el estado actual en la imagen |
| `archie` | Chat directo con el modelo vía Ollama |

---

## FASE 7 — EDITAR CONFIGURACIÓN

**Regla crítica:** nunca editar `openclaw.json` desde el host con nano/vim.
El sistema de permisos VFS + Podman rootless cambia el dueño del archivo
a `nobody` cuando se escribe desde el host, rompiendo el acceso de OpenClaw.

**Siempre editar desde dentro del contenedor:**

```bash
abrahack-shell
vi /root/.openclaw/openclaw.json
# o usar openclaw config set
openclaw config set agents.defaults.model.primary "ollama/qwen2.5:7b-instruct-q4_K_M"
```

Después de cualquier cambio de config, guardar el estado:

```bash
# Desde el host
abrahack-save
```

---

## FLUJO OPERATIVO DIARIO

```bash
# Iniciar sesión de trabajo
abrahack                    # abre TUI del agente

# Al terminar, guardar cambios si los hubo
abrahack-save

# Si Ollama está caído
sudo systemctl start ollama

# Para reconfigurar
abrahack-shell              # entrar a bash
vi /root/.openclaw/openclaw.json
exit
abrahack-save               # guardar
podman restart openclaw-agent
abrahack                    # volver a entrar
```

---

## APÉNDICE — ELIMINAR OPENCLAW COMPLETAMENTE

Para desinstalar OpenClaw y limpiar todos sus componentes del sistema:

### 1. Detener y eliminar contenedores

```bash
podman stop openclaw-agent 2>/dev/null
podman rm openclaw-agent 2>/dev/null
```

### 2. Eliminar imágenes

```bash
podman rmi abrahack/openclaw-configured 2>/dev/null
podman rmi abrahack/openclaw-agent 2>/dev/null
podman rmi docker.io/library/node:24-alpine 2>/dev/null
```

### 3. Limpiar storage de Podman

```bash
podman system prune -af
rm -rf ~/.local/share/containers/storage
```

### 4. Eliminar archivos de configuración de Podman

```bash
rm -rf ~/.config/containers
```

### 5. Eliminar directorio del laboratorio

```bash
rm -rf ~/abrahack-agent
rm -rf ~/.openclaw-data  # si existe de intentos anteriores
```

### 6. Eliminar aliases del shell

```bash
# Editar ~/.zshrc y eliminar el bloque "Abrahack Lab — OpenClaw"
nano ~/.zshrc
source ~/.zshrc
```

### 7. Desinstalar Podman (opcional)

Solo si no lo usas para nada más:

```bash
sudo pacman -Rns podman podman-compose
yay -Rns docker-rootless-extras 2>/dev/null
```

### 8. Revertir configuración de Ollama (opcional)

Si quieres que Ollama vuelva a escuchar solo en localhost:

```bash
sudo rm /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama
ss -tlnp | grep 11434
# Debe mostrar: 127.0.0.1:11434
```

### 9. Verificar limpieza completa

```bash
podman ps -a           # sin contenedores openclaw
podman images          # sin imágenes abrahack
ls ~/.config/containers 2>/dev/null || echo "limpio"
ls ~/abrahack-agent 2>/dev/null || echo "limpio"
```

---

*Documento generado para Abrahack Lab — Mayo 2026*  
*Stack validado: Arch Linux 7.0.9 · Podman 5.8.2 · OpenClaw 2026.5.22 · Ollama + qwen2.5:7b-instruct-q4_K_M*
