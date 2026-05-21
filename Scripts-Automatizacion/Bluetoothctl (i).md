# Bluetooth-Manager-OpenClaw

## Idea
Automatizar la gestión de dispositivos Bluetooth desde terminal mediante un script
inteligente que elimine la necesidad de entrar al intérprete interactivo de bluetoothctl.
Eventualmente ejecutable desde OpenClaw con lenguaje natural.

## Trigger
- Comando directo: `btconnect "Mi Auricular"`
- Comando desde OpenClaw: *"conecta mis audífonos"*
- Autoconexión al iniciar Hyprland para dispositivos de confianza

## Herramientas
- [x] Script bash
- [ ] Claude API
- [x] OpenClaw
- [ ] Otro:

## Contexto Técnico
`bluetoothctl` opera como intérprete interactivo, lo que dificulta su automatización.
La solución es usar el modo no-interactivo pasando comandos por pipe:

```bash
# Ejemplo de uso no-interactivo
echo -e "power on\nscan on\n" | bluetoothctl
bluetoothctl connect AA:BB:CC:DD:EE:FF
```

## Pasos de Implementación

1. Crear script `btconnect` que reciba nombre o MAC del dispositivo
2. Si recibe nombre, buscar la MAC en `paired-devices` automáticamente
3. Ejecutar secuencia: `power on` → `connect MAC`
4. Confirmar conexión exitosa y notificar con `dunst`
5. Integrar como comando de OpenClaw

## Comandos Base (bluetoothctl)

| Acción | Comando |
| :--- | :--- |
| Encender adaptador | `bluetoothctl power on` |
| Escanear dispositivos | `bluetoothctl scan on` |
| Emparejar | `bluetoothctl pair AA:BB:CC:DD:EE:FF` |
| Conectar | `bluetoothctl connect AA:BB:CC:DD:EE:FF` |
| Marcar confianza | `bluetoothctl trust AA:BB:CC:DD:EE:FF` |
| Ver emparejados | `bluetoothctl paired-devices` |
| Desconectar | `bluetoothctl disconnect AA:BB:CC:DD:EE:FF` |

## Script Objetivo (borrador)

```bash
#!/bin/bash
# btconnect — Conectar dispositivo Bluetooth por nombre
# Uso: btconnect "Mi Auricular"

DEVICE_NAME="$1"
MAC=$(bluetoothctl paired-devices | grep "$DEVICE_NAME" | awk '{print $2}')

if [ -z "$MAC" ]; then
    echo "Dispositivo no encontrado: $DEVICE_NAME"
    exit 1
fi

bluetoothctl power on
bluetoothctl connect "$MAC"
notify-send "Bluetooth" "Conectado: $DEVICE_NAME"
```

## Estado
#idea #bluetooth #automatizacion #openclaw

## Fecha
2026-05-20

## Links
- [[Arch]] → PARTE 5 Bluetooth
- [[6. OpenClaw_Lab_Setup_Abrahack]]