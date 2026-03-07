
# ABRAHACK LAB — INSTALACIÓN DEL ENTORNO OPENCLAW EN CONTENEDOR AISLADO

## OBJETIVO

Construir un contenedor de laboratorio completamente funcional para ejecutar **OpenClaw** dentro de la infraestructura de **Abrahack**, utilizando **Podman** y un entorno Debian aislado.

Este documento describe:

- Creación del contenedor
- Resolución de errores de `apt` en entornos rootless
- Instalación de dependencias base
- Preparación del entorno para instalar OpenClaw
- Base para construir posteriormente una **imagen reutilizable de laboratorio**

------------------------------------------------------------------------

# 1. ARQUITECTURA DEL LABORATORIO

El laboratorio utiliza un modelo de **aislamiento por contenedor**.

Componentes principales:

Host
↓
Podman (rootless)
↓
Contenedor Debian
↓
Runtime de herramientas
↓
OpenClaw

Ventajas:

- Aislamiento del sistema base
- Reproducibilidad del laboratorio
- Creación futura de imágenes reutilizables
- Integración con la plataforma Abrahack

------------------------------------------------------------------------

# 2. CREACIÓN DEL CONTENEDOR BASE

Se utiliza la imagen oficial de Debian.

```bash
podman run -it --name openclaw --privileged docker.io/debian:bookworm bash
```

Esto inicia un contenedor interactivo.

Prompt esperado:

```
root@container:/#
```

------------------------------------------------------------------------

# 3. ERROR DETECTADO DURANTE LA INSTALACIÓN

Durante la ejecución de:

```bash
apt update
```

aparece el error:

```
setgroups 65534 failed
setegid 65534 failed
Method http has died unexpectedly
```

Esto ocurre porque:

- Podman se ejecuta en **modo rootless**
- `apt` intenta cambiar al usuario `_apt`
- el kernel bloquea `setgroups()` dentro del namespace de usuario

Resultado: el downloader de `apt` falla.

------------------------------------------------------------------------

# 4. SOLUCIÓN APLICADA

Se desactiva el sandbox de usuario de `apt` para ejecutar las descargas como root.

Dentro del contenedor:

```bash
echo 'APT::Sandbox::User "root";' > /etc/apt/apt.conf.d/99sandboxroot
```

Esto evita que `apt` cambie al usuario `_apt`.

------------------------------------------------------------------------

# 5. ACTUALIZACIÓN DEL SISTEMA

Ahora `apt` funciona correctamente.

```bash
apt update
```

------------------------------------------------------------------------

# 6. INSTALACIÓN DE DEPENDENCIAS BASE

Instalar herramientas necesarias para el laboratorio:

```bash
apt install -y curl git build-essential
```

Estas herramientas permiten:

curl → descargar recursos externos  
git → clonar repositorios  
build-essential → compilar dependencias

------------------------------------------------------------------------

# 7. INSTALACIÓN DE NODEJS

OpenClaw utiliza NodeJS.

Instalar repositorio oficial:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
```

Instalar Node:

```bash
apt install -y nodejs
```

Verificar instalación:

```bash
node -v
npm -v
```

------------------------------------------------------------------------

# 8. ESTRUCTURA DEL LABORATORIO

Se recomienda crear una estructura interna para el laboratorio.

```bash
mkdir /lab
cd /lab
```

Estructura sugerida:

Carpeta | Función
--------|--------
openclaw | código fuente
logs | registros del sistema
tools | herramientas auxiliares
tmp | ejecuciones temporales

Ejemplo:

```bash
mkdir openclaw logs tools tmp
```

------------------------------------------------------------------------

# 9. PREPARACIÓN PARA INSTALAR OPENCLAW

Clonar el repositorio:

```bash
git clone <repositorio-openclaw>
cd openclaw
```

Instalar dependencias:

```bash
npm install
```

Ejecutar el servicio:

```bash
npm start
```

------------------------------------------------------------------------

# 10. VERIFICACIÓN DEL ENTORNO

Confirmar que el laboratorio tiene:

✔ Debian funcionando  
✔ apt operativo  
✔ NodeJS instalado  
✔ herramientas base disponibles  
✔ estructura de laboratorio creada

Si todo está correcto el contenedor ya está listo para ejecutar OpenClaw.

------------------------------------------------------------------------

# 11. SIGUIENTE FASE (IMAGEN DE LABORATORIO)

Una vez validado el entorno se creará una **imagen base reutilizable**.

Flujo futuro:

Host
↓
Podman Image → `abrahack-openclaw-lab`
↓
Instancias de laboratorio
↓
Usuarios de la plataforma

Esto permitirá lanzar laboratorios con:

```bash
podman run abrahack-openclaw-lab
```

Ventajas:

- despliegue instantáneo
- consistencia del entorno
- escalabilidad para múltiples estudiantes

------------------------------------------------------------------------

# ESTADO ACTUAL

ENTORNO LISTO PARA INSTALAR OPENCLAW

Contenedor funcional
APT corregido
Dependencias instaladas
Base preparada para construir imagen reutilizable

------------------------------------------------------------------------
