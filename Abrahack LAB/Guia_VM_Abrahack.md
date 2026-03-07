# ABRAHACK LAB --- GUIA OFICIAL DE IMPLEMENTACION VM KALI

## 1. OBJETIVO

Establecer un entorno virtual seguro, optimizado y modular para
experimentación con agentes cognitivos, automatización e infraestructura
Abrahack.

------------------------------------------------------------------------

## 2. REQUISITOS DE HARDWARE HOST

  Recurso   Recomendado
  --------- ----------------
  CPU       4+ hilos
  RAM       8 GB
  GPU       Opcional
  Disco     ≥100 GB libres

Configuración objetivo aplicada:

-   CPU → 4 threads
-   RAM → 4096 MB
-   Disco → 80 GB dinámico

------------------------------------------------------------------------

## 3. CREACION DE MAQUINA VIRTUAL

Tipo: Linux\
Versión: Debian 64-bit

Disco: VDI dinámico

Red: NAT

Aceleración: - VT-x activo - Nested paging activo

------------------------------------------------------------------------

## 4. INSTALACION SISTEMA OPERATIVO

Modo instalación: Graphical Install

Configuración usuario: - usuario estándar (no root)

Particionado: Guided → entire disk → encrypted LVM

Bootloader: Instalar GRUB en /dev/sda

------------------------------------------------------------------------

## 5. SELECCION DE COMPONENTES

Seleccionar únicamente:

-   Xfce Desktop
-   Standard system utilities
-   Top 10 tools

No seleccionar:

-   Entornos pesados
-   Colecciones completas
-   Servidores innecesarios

------------------------------------------------------------------------

## 6. ACTUALIZACION INICIAL

Ejecutar:

sudo apt update && sudo apt upgrade -y

Instalar base:

sudo apt install git curl wget build-essential -y

------------------------------------------------------------------------

## 7. OPTIMIZACION DE RENDIMIENTO

Reducir uso swap:

Archivo: /etc/sysctl.conf

Agregar: vm.swappiness=10

Aplicar: sudo sysctl -p

------------------------------------------------------------------------

## 8. HARDENING BASICO

Instalar firewall:

    sudo apt install ufw -y

Configurar:

    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw enable

------------------------------------------------------------------------

## 9. SNAPSHOT BASE

Crear snapshot inicial llamado:

CleanBase

Proposito: Restauracion inmediata a estado limpio.

------------------------------------------------------------------------

## 10. PRINCIPIOS OPERATIVOS DEL LABORATORIO

Reglas:

1.  Sistema minimo primero
2.  Modulos bajo demanda
3.  Automatizacion despues de estabilidad
4.  Agentes siempre en sandbox
5.  Logs obligatorios

------------------------------------------------------------------------

## 11. ARQUITECTURA BASE DEL SISTEMA

Estructura inicial:

OpenClaw ↓ Interpreter ↓ Tool Selector ↓ Sandbox Runner ↓ Logs

------------------------------------------------------------------------

## 12. FILOSOFIA DE EXPANSION

Orden correcto:

Estabilidad → Control → Automatizacion → Escala

Nunca invertir este orden.

------------------------------------------------------------------------

## 13. ESTADO FINAL ESPERADO

Al completar esta fase el sistema debe estar:

-   Estable
-   Ligero
-   Seguro
-   Modular
-   Versionable
-   Recuperable

------------------------------------------------------------------------

## 14. PROXIMA FASE

Implementacion del entorno de ejecucion controlado para agentes:

Sandbox + Limites + Auditoria.
