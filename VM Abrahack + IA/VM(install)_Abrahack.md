# ABRAHACK LAB --- GUIA OFICIAL DE IMPLEMENTACION VM KALI

##  OBJETIVO

Establecer un entorno virtual seguro, optimizado y modular para
experimentación con agentes cognitivos, automatización e infraestructura
Abrahack.

------------------------------------------------------------------------

##  REQUISITOS MINIMOS DE HARDWARE HOST

  CPU       4+ hilos
  RAM       8 GB
  GPU       Opcional
  Disco     ≥100 GB libres

## CONFIGURACIÓN OBJETIVO APLICADA

    -   CPU → 4 threads
    -   RAM → 4096 MB
    -   Disco → 100 GB dinámico

------------------------------------------------------------------------

## 1. MAQUINA VIRTUAL

Tipo: Linux\
Versión: Debian 64-bit

Disco: VDI dinámico

Red: NAT

Aceleración: - VT-x activo - Nested paging activo

------------------------------------------------------------------------

## 2. INSTALACION SISTEMA OPERATIVO

### S.O
- Descarga Kali Linux (imagen oficial)
- Instala Oracle VM VirtualBox de Oracle si no lo tienes.
- Abre VirtualBox → New  → Nombre:AbrahackLab → Tipo: Linux → Versión: Debian (64-bit)

### Configuración HW
- RAM: 4096 MB  → CPU  → 4 nucleos  
- Disco: VDI → Asignación: Dinamica → Tamaño : 100 GB

### Ajustes avanzados VM
- Processor: ✔ Enable PAE/NX
- Acceleration: ✔ VT-x/AMD-V enabled ✔ Nested paging enabled
- Display: Video Memory 128 MB → Graphics controller: VMSVGA 
- Network: NAT

### Montar ISO e instalar Sistema: 
- Settings → Storage → Empty → icon CD → choose ISO → Graphical Install
- Idioma:  el tuyo → Zona horaria: automática
- Usuario: El que quieras (no uses root) Ej: Analyst
- Disco: Guided – use entire disk → Esquema: All files in one partition 
    
    Podriamos usar: Guided – use entire disk and Setup encrypted LVM para: 
    - Cifrar todo el disco virtual
    - Usar LUKS como capa de cifrado
    - Montar el sistema solo tras introducir contraseña
    - Proteger datos en reposo

 Si alguien copia tu archivo .vdi → no puede leer nada

 DESKTOP ENVIRONMENT: 
 ✔ standard system utilities
 ✔ Top 10 tools
 ✔ Xfce

 Instalar el GRUB Boot Loader → Select device for boot loader installation: /dev/sda

- Software selection: Marca solo ✔ standard system utilities

------------------------------------------------------------------------

## 3. ARRANQUE OPTIMIZADO

### Actualiza sistema e instala herramientas base

```bash
sudo apt update && sudo apt upgrade -y
```
```bash
sudo apt install git curl wget build-essential -y
```

### Optimización de rendimiento
- Reducir consumo RAM
```bash
sudo nano /etc/sysctl.conf
```
Agregar:
```bash
vm.swappiness=10
```
Guardar

Aplicar
```bash
sudo sysctl -p
```
Desactivar servicios innecesarios:
Aplicar
```bash
systemctl list-unit-files --type=service | grep enabled
```
Desactiva los que no uses

### Seguridad base

Instala firewall
```bash
sudo apt install ufw -y
```

Activar:
```bash
sudo ufw enable
```

Permitir solo salidas:
```bash
sudo ufw default allow outgoing
sudo ufw default deny incoming
```

Verificar estado:
```bash
sudo ufw status verbose
```
Tu salida deberia verse así:

```bash
Status: active

Default:
 deny (incoming)
 allow (outgoing)
 deny (routed)
```

Asegura el Loopback explicito: 
(Viene por defecto pero verificalo)

```bash
sudo ufw allow in on lo
```

Realiza una prueba de seguridad:

```bash
sudo nmap localhost
```
Salida: All ports filtered



 ## 4. SNAPSHOT INICIAL (IMPORTANTE)
 - Nombre: Cleanbase

```bash

```

##  PROXIMA FASE

Implementacion del entorno de ejecucion asilado para agentes:

Sandbox + Limites + Auditoria.
