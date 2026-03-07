# ABRAHACK LAB --- MODULO DE CONTROL DE EJECUCION SEGURO

------------------------------------------------------------------------

## 1. PROPOSITO DEL MODULO

Establecer una capa de ejecución controlada que limite el impacto de
procesos autónomos, scripts o agentes cognitivos dentro del laboratorio.

Este módulo constituye la primera barrera real de seguridad operativa
del sistema.

Principio rector:

    Ningún agente ejecuta procesos directamente en el sistema.

------------------------------------------------------------------------

## 2. ARQUITECTURA CONCEPTUAL

Estructura lógica:

Host OS └── VM └── Usuario aislado └── Wrapper seguro └── Proceso
ejecutado

El wrapper actúa como intermediario obligatorio entre el agente y el
sistema.

------------------------------------------------------------------------

## 3. CREACION DE USUARIO AISLADO

Objetivo: Separar contexto operativo humano del contexto automatizado.

Comando:

    sudo adduser agent

Permisos administrativos controlados:

    sudo usermod -aG sudo agent

Justificación: Si el agente se compromete, el sistema principal
permanece intacto.

------------------------------------------------------------------------

## 4. DIRECTORIO SANDBOX BASE

Creación:

    sudo mkdir -p /opt/abrahack
    sudo chown agent:agent /opt/abrahack
    sudo chmod 700 /opt/abrahack

Significado permisos 700:

Propietario = acceso total\
Grupo = sin acceso\
Otros = sin acceso

Resultado: Espacio privado inaccesible desde otros usuarios.

------------------------------------------------------------------------

## 5. LIMITACION DE RECURSOS DEL USUARIO

Archivo:

    /etc/security/limits.conf

Configuración:

    agent hard nproc 150
    agent hard cpu 50
    agent hard rss 2048000
    agent hard nofile 1024

Definiciones:

nproc → máximo procesos simultáneos\
cpu → segundos de CPU permitidos\
rss → RAM máxima en KB\
nofile → archivos abiertos simultáneamente

Objetivo: Prevenir saturación del sistema.

------------------------------------------------------------------------

## 6. ESTRUCTURA INTERNA

Directorios:

    runtime
    logs
    tools
    tmp

Principio: Modularidad = control + trazabilidad.

------------------------------------------------------------------------

## 7. WRAPPER DE EJECUCION SEGURA

Archivo:

    /opt/abrahack/run_safe.sh

Contenido:

#!/bin/bash ulimit -u 100 ulimit -n 512 ulimit -t 30 ulimit -v 1500000
timeout 40s "\$@"

------------------------------------------------------------------------

## 8. ANALISIS DE PARAMETROS

ulimit -u 100\
Limita procesos hijos → evita forks infinitos.

ulimit -n 512\
Limita archivos abiertos → evita saturación de sockets.

ulimit -t 30\
Limita tiempo CPU → mata loops intensivos.

ulimit -v 1500000\
Limita memoria virtual (\~1.5GB).

timeout 40s\
Límite total de ejecución real.

------------------------------------------------------------------------

## 9. CPU TIME vs REAL TIME

CPU time = tiempo de cálculo real\
Real time = tiempo total transcurrido

Ambos límites juntos evitan:

-   loops
-   procesos congelados
-   scripts dormidos

------------------------------------------------------------------------

## 10. USO OPERATIVO

Formato:

    /opt/abrahack/run_safe.sh comando

Ejemplo:

    /opt/abrahack/run_safe.sh ping google.com

------------------------------------------------------------------------

## 11. ALIAS OPERATIVO

Agregar a \~/.bashrc:

    alias safe='/opt/abrahack/run_safe.sh'

Uso:

    safe comando

------------------------------------------------------------------------

## 12. PROPIEDADES DE SEGURIDAD

El sistema ahora posee:

-   control de recursos
-   aislamiento de usuario
-   ejecución controlada
-   límites automáticos
-   entorno modular

------------------------------------------------------------------------

## 13. ESTADO DEL SISTEMA

Nivel actual:

    BASE SEGURA OPERATIVA

El entorno puede ejecutar código desconocido con riesgo limitado.

------------------------------------------------------------------------

## 14. REGLA DE LABORATORIO

Si un proceso no pasa por el wrapper:

    NO se ejecuta.

------------------------------------------------------------------------

## 15. SIGUIENTE FASE

Implementación de contenedor aislado para herramientas.

------------------------------------------------------------------------

FIN DEL DOCUMENTO
