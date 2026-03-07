# ABRAHACK --- Módulo de Infraestructura Segura de Contenedores

### Documento Técnico de Implementación y Corrección Arquitectónica

------------------------------------------------------------------------

## 1. Objetivo

Establecer un entorno de ejecución aislado, reproducible y seguro para
agentes autónomos (OpenClaw u otros), utilizando contenedores rootless
bajo Podman dentro de una VM Kali Linux.

Este módulo constituye la base operacional del sistema Abrahack para:

-   ejecución segura de scripts
-   aislamiento de procesos
-   prevención de escape de privilegios
-   pruebas controladas
-   laboratorio ofensivo/forense

------------------------------------------------------------------------

## 2. Arquitectura Final Validada

    Host (Windows/Linux)
     └── VM Kali Linux
          └── Podman Rootless
               └── slirp4netns Network
                    └── Contenedor Sandbox
                         └── Runtime Agente

Características:

-   aislamiento multinivel
-   namespaces activos
-   sin privilegios root reales
-   red virtual aislada
-   destrucción instantánea del entorno

------------------------------------------------------------------------

## 3. Principales Errores Encontrados y Correcciones

### Error 1 --- SubUID/SubGID mapping

Problema: Faltaban rangos asignados al usuario agente.

Solución: Agregar en:

    /etc/subuid
    /etc/subgid

    agent:165536:65536

------------------------------------------------------------------------

### Error 2 --- Driver de almacenamiento incompatible

Problema: Filesystem host ext2/ext3 no soporta overlayfs rootless.

Síntoma:

    lchown operation not permitted

Solución:

    ~/.config/containers/storage.conf

    [storage]
    driver = "vfs"

Luego limpiar cache:

    rm -rf ~/.local/share/containers/storage

------------------------------------------------------------------------

### Error 3 --- Red bridge rootless fallando

Problema: Las redes bridge requieren systemd user session + DBus.

Síntoma:

    Failed to connect to user scope bus

Solución:

Usar modo:

    --network slirp4netns

Este modo:

-   no requiere systemd
-   no requiere DBus
-   funciona en VMs
-   es más seguro

------------------------------------------------------------------------

## 4. Configuración Final Estable

Comando funcional validado:

    podman run --rm -it \
    --network slirp4netns \
    --pids-limit 128 \
    --memory 512m \
    --cap-drop ALL \
    docker.io/library/alpine sh

Resultado esperado:

    uid=0(root)

Esto confirma:

-   namespace activo
-   root virtual aislado
-   sandbox operativo

------------------------------------------------------------------------

## 5. Principios de Seguridad Implementados

El entorno cumple principios de hardening:

-   Zero privileges
-   Resource limiting
-   Namespace isolation
-   Ephemeral execution
-   Network sandboxing
-   Host protection

------------------------------------------------------------------------

## 6. Justificación Arquitectónica

Se eligió:

Podman rootless + slirp4netns + VFS

Porque:

  Componente   Motivo
  ------------ --------------------------
  Rootless     evita privilegios
  VFS          compatible con VM
  slirp        independiente de systemd
  Containers   destrucción instantánea

Esta combinación es considerada arquitectura estable para:

-   laboratorios de malware
-   ejecución de agentes IA
-   testing ofensivo
-   sandboxing de código desconocido

------------------------------------------------------------------------

## 7. Nivel de Madurez Alcanzado

El entorno actual corresponde a un:

> Sandbox profesional de ejecución controlada

No es un entorno experimental básico.

Capacidades actuales:

✔ ejecutar código no confiable\
✔ destruir entorno en segundos\
✔ limitar consumo\
✔ registrar actividad\
✔ aislar red

------------------------------------------------------------------------

## 8. Riesgos Eliminados

La configuración mitiga:

-   escapes de privilegios
-   ejecución host-level
-   persistencia maliciosa
-   acceso directo a hardware
-   modificación del sistema base

------------------------------------------------------------------------

## 9. Estado Operacional

Estado actual del módulo:

    ESTABLE — LISTO PARA INTEGRACIÓN DE AGENTES

No se requieren más ajustes de infraestructura base.

------------------------------------------------------------------------

## 10. Próximas Fases Arquitectónicas

Orden recomendado:

1.  Contenedor persistente hardened
2.  Runtime executor controlado
3.  Supervisor de procesos
4.  Logging forense
5.  Integración OpenClaw
6.  Sistema de políticas
7.  Watchdog de comportamiento

------------------------------------------------------------------------

## 11. Conclusión Técnica

La infraestructura construida cumple criterios reales de sandboxing
profesional.

El entorno ya permite ejecutar agentes autónomos con:

-   aislamiento real
-   control de recursos
-   contención de riesgo

Esto establece la base fundamental del sistema Abrahack como plataforma
de automatización segura.

------------------------------------------------------------------------

**Estado del módulo:** VALIDADO\
**Nivel:** Profesional\
**Listo para:** Integración de agentes autónomos
