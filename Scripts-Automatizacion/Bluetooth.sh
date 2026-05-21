#!/bin/bash

# Función para enviar notificaciones consistentes en Hyprland
notificar() {
    notify-send "Bluetooth" "$1" --icon="$2"
    echo "$1"
}

# Mostrar ayuda si no hay argumentos
if [ -z "$1" ]; then
    echo "Abrahack OS - Controlador de Bluetooth"
    echo "Uso:"
    echo "  bluetooth on                 # Enciende el adaptador Bluetooth"
    echo "  bluetooth off                # Apaga el adaptador Bluetooth"
    echo "  bluetooth status             # Muestra el estado del Bluetooth"
    echo "  bluetooth <Nombre/Alias>     # Conecta un dispositivo emparejado"
    echo "  bluetooth disconnect <Name>  # Desconecta un dispositivo específico"
    exit 0
fi

# ACCIÓN: Encender Bluetooth Global
if [ "$1" == "on" ]; then
    bluetoothctl power on &> /dev/null
    notificar "Adaptador Bluetooth: ENCENDIDO" "bluetooth"
    exit 0
fi

# ACCIÓN: Apagar Bluetooth Global
if [ "$1" == "off" ]; then
    bluetoothctl power off &> /dev/null
    notificar "Adaptador Bluetooth: APAGADO" "bluetooth-disabled"
    exit 0
fi

# ACCIÓN: Ver estado actual
if [ "$1" == "status" ]; then
    echo "=== Estado del Controlador ==="
    bluetoothctl show | grep -E "Powered|Discoverable|Pairable"
    echo "=== Dispositivos Conectados Actualmente ==="
    bluetoothctl devices Connected
    exit 0
fi

# ACCIÓN: Desconectar un dispositivo específico
if [ "$1" == "disconnect" ] || [ "$1" == "desc" ]; then
    if [ -z "$2" ]; then
        echo "❌ Error: Especifica el nombre del dispositivo a desconectar."
        echo "Ejemplo: bluetooth disconnect audifonos"
        exit 1
    fi
    
    DEVICE_NAME="$2"
    # CORRECCIÓN: Buscamos en 'devices' para que detecte alias locales
    MAC=$(bluetoothctl devices | grep -i "$DEVICE_NAME" | awk '{print $2}')
    
    if [ -z "$MAC" ]; then
        echo "❌ Dispositivo no encontrado: $DEVICE_NAME"
        exit 1
    fi
    
    if bluetoothctl disconnect "$MAC" &> /dev/null; then
        notificar "Desconectado de: $DEVICE_NAME" "bluetooth"
    else
        notificar "Error al intentar desconectar $DEVICE_NAME" "error"
        exit 1
    fi
    exit 0
fi

# ACCIÓN POR DEFECTO: Conectar dispositivo
DEVICE_NAME="$1"
# CORRECCIÓN: Buscamos en 'devices' para que detecte alias locales
MAC=$(bluetoothctl devices | grep -i "$DEVICE_NAME" | awk '{print $2}')

if [ -z "$MAC" ]; then
    echo "❌ Dispositivo no encontrado entre los registrados: $DEVICE_NAME"
    exit 1
fi

# Asegurar encendido previo
bluetoothctl power on &> /dev/null

if bluetoothctl connect "$MAC" &> /dev/null; then
    notificar "Conectado exitosamente a: $DEVICE_NAME" "bluetooth"
else
    notificar "Fallo en la conexión con $DEVICE_NAME." "error"
    exit 1
fi