#!/bin/bash

clear
echo "====================================================="
echo "    Abrahack OS - Escáner Inteligente Bluetooth      "
echo "====================================================="

# 1. Asegurar que el adaptador esté encendido
bluetoothctl power on &> /dev/null

echo "🔍 Escaneando el aire por 10 segundos... Filtrando nombres..."
echo "Por favor, espera a que termine para poder elegir con calma."
echo "-----------------------------------------------------"
echo -e "  \e[1;34mDIRECCIÓN MAC\e[0m       |  \e[1;32mNOMBRE DEL DISPOSITIVO\e[0m"
echo "-----------------------------------------------------"

# 2. El Truco Pro: Escanea en segundo plano, filtramos con grep/awk para limpiar la salida,
# eliminamos duplicados con 'sort -u' y guardamos el resultado temporalmente.
bluetoothctl scan on &> /dev/null &
SCAN_PID=$!

# Dejar que escanee por 10 segundos acumulando dispositivos
sleep 10

# Apagar el escáner limpiamente
kill $SCAN_PID &> /dev/null
bluetoothctl scan off &> /dev/null

# Extraer los dispositivos encontrados del buffer del sistema
bluetoothctl devices | sort -u | grep -v "Device  " | while read -r line; do
    MAC=$(echo "$line" | awk '{print $2}')
    NAME=$(echo "$line" | cut -d' ' -f3-)
    if [ ! -z "$NAME" ]; then
        printf "  %-18s |  %s\n" "$MAC" "$NAME"
    fi
done

echo "-----------------------------------------------------"
echo "-> Escaneo completado de forma legible."
echo ""

# 3. Solicitar los datos para automatizar el resto de tus comandos
read -p "📌 Pega la dirección MAC del dispositivo que quieres configurar: " MAC

if [ -z "$MAC" ]; then
    echo "❌ Operación cancelada. No ingresaste ninguna MAC."
    exit 1
fi

read -p "📌 ¿Qué alias/nombre corto le quieres dar? (ej. audifonos): " ALIAS

if [ -z "$ALIAS" ]; then
    echo "❌ Operación cancelada. El alias es obligatorio."
    exit 1
fi

echo ""
echo "-> Iniciando secuencia automática para: $ALIAS ($MAC)"
echo "-----------------------------------------------------"

# 4. Correr tus comandos en orden capturando confirmaciones automáticamente
echo "1/4 -> Emparejando (pair)..."
# Usamos un pipe con 'yes' por si el prompt pide confirmación manual de llaves
echo "yes" | bluetoothctl pair "$MAC"

echo "2/4 -> Guardando en confianza (trust)..."
bluetoothctl trust "$MAC" &> /dev/null

echo "3/4 -> Asignando alias personalizado..."
bluetoothctl set-alias "$ALIAS" &> /dev/null

echo "4/4 -> Ejecutando primera conexión..."
if bluetoothctl connect "$MAC" &> /dev/null; then
    echo "-----------------------------------------------------"
    echo "🎉 ¡ÉXITO TOTAL! Tu dispositivo está configurado."
    echo "🚀 Ya puedes usar en cualquier momento: blueconnect $ALIAS"
    notify-send "Bluetooth Setup" "Dispositivo '$ALIAS' emparejado y conectado."
else
    echo "-----------------------------------------------------"
    echo "⚠️  Estructura guardada con éxito, pero la conexión inicial falló."
    echo "Asegúrate de que el dispositivo esté encendido y corre: blueconnect $ALIAS"
fi
