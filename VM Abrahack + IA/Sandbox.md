# ABRAHACK LAB --- GUIA DE IMPLEMENTACIÓN ENTORNO AISLADO PARA AGENTES

## OBJETIVO

Crear un entorno aislado donde luego correrá el agente sin tocar tu sistema base.

------------------------------------------------------------------------

## 1. CREAR USUARIO AISLADO PARA AGENTES

### Crear usuario dedicado

```bash
sudo adduser agent
```
password → crea uno fuerte

### Crear directorio sandbox

Solo el usuario agent podra acceder
```bash
sudo mkdir -p /opt/abrahack
sudo chown agent:agent /opt/abrahack
sudo chmod 700 /opt/abrahack
```
### Limitar recursos del usuario agente

Limita procesos
Limita CPU
Limita RAM
Limita archivos abiertos

```bash
sudo nano /etc/security/limits.conf
```
Agrega al final
```bash
agent hard nproc 150
agent hard cpu 50
agent hard rss 2048000
agent hard nofile 1024
```
Guardar → CTRL+O → Enter → CTRL+X

### Crear entorno runtime

Entra como agente
```bash
su - agent
```

Crear estructura
Carpeta	→ Función
runtime → Procesos activos
logs	→ Auditoría
tools	→ Herramientas y scripts
tmp	    → Ejecuciones temporales

```bash
mkdir runtime logs tools tmp
```

### Crear wrapper de ejecución segura
Sal del usuario → exit

Crea un ejecutor
```bash
#!/bin/bash
ulimit -u 100
ulimit -n 512
ulimit -t 30
ulimit -v 1500000

timeout 40s "$@"
```
Guarda y otorga permisos

```bash
sudo chmod +x /opt/abrahack/run_safe.sh
sudo chown agent:agent /opt/abrahack/run_safe.sh
```
Cuando uses el agente en el futuro, nunca ejecutará comandos directo
```bash
/opt/abrahack/run_safe.sh comando
ej: /opt/abrahack/run_safe.sh nmap localhost
```

### Crea un alias de ejecución (Recomendado)
Agrega el alias al usuario agent
```bash
nano ~/.bashrc
```
Agrega al final
```bash
alias safe='/opt/abrahack/run_safe.sh'
```
aplica
```bash
source ~/.bashrc
```

# ABRAHACK LAB --- GUIA DE IMPLEMENTACIÓN CONTENEDOR AISLADO PARA HERRAMIENTAS 

Motor de contenedor: Podman rootless
No hay daemon.
No hay root global.
Cada contenedor pertenece a un usuario.
Eso significa que dentro del contenedor puedes ser root… pero fuera eres usuario normal.

## OBJETIVO

añadirá aislamiento real de: filesystem, red, procesos, permisos

## 1. INSTALACIÓN DE PODMAN ROOTLESS

### Preparar dependencias base

uidmap → permite namespaces de usuario
slirp4netns → red rootless
fuse-overlayfs → filesystem aislado
podman	→ motor contenedores

```bash
sudo apt update
sudo apt install podman uidmap slirp4netns fuse-overlayfs -y
```

### Configurar subuids/subgids para usuario agent

Esto define el rango de IDs virtuales dentro del contenedor.

```bash
sudo nano /etc/subuid
```
Agregar línea
```bash
agent:165536:65536
```

Ahora
```bash
sudo nano /etc/subgid
```

Agregar línea
```bash
agent:165536:65536
```

### Verificar modo rootless
Cambia a usuario agent
```bash
su - agent
```
Ejecuta
```bash
podman info
```
Salida → rootless: true

### Crear entorno contenedores

Esto separa el runtime del sistema global

Como usuario agent
```bash
mkdir -p ~/.config/containers
mkdir -p ~/.local/share/containers
```

### Configuración hardened

Crear archivo
```bash
nano ~/.config/containers/containers.conf
```

Contenido

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

De esta manera:
- no ve procesos host
- no ve hostname real
- no comparte IPC
- no tiene capacidades kernel
- no puede escalar privilegios

### Red aislada segura

Verifica
```bash
podman network ls
```

## 2. ELIMINAR LIMITACIONES DE KERNEL

Configurar Podman que use un driver de almacenamiento compatible. 
driver VFS funciona en cualquier FS porque:
no usa overlayfs ni chown complejo, es más lento, pero más compatible y seguro para laboratorio.

### Crear config storage

Como usuario: agent
```bash
mkdir -p ~/.config/containers
nano ~/.config/containers/storage.conf
```

Edita y guarda
```bash
[storage]
driver = "vfs"
```

Limpia Storage anterior
```bash
rm -rf ~/.local/share/containers/storage
```

### Contenedor de prueba hardened

Probamos el aislamiento

```bash
podman run --rm -it --network slirp4netns alpine sh
```

Dentro del contenedor ejecuta
```bash
id
```

Salida
```bash
uid=0(root)
```

Ahora prueba
```bash
cat /etc/shadow
```
Salida →  Exit

```bash
mkdir -p ~/.config/containers
nano ~/.config/containers/storage.conf
```