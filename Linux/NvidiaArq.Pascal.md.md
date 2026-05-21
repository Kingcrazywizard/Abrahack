### Paso 1: Asegurar que tienes las cabeceras del Kernel

Como el paquete del AUR va a fabricar el driver exclusivo para tu sistema, necesitas los archivos de desarrollo de tu Kernel. Si estás usando el Kernel normal, corre:

Bash

```
sudo pacman -S linux-headers
```

_(Si decidiste quedarte en el Kernel LTS, instala `linux-lts-headers`)_.

### Paso 2: Instalar el driver heredado correcto desde el AUR

En la noticia mencionan la rama `nvidia-580xx-dkms`. Vamos a pedirle a tu asistente de AUR (`yay`) que la descargue, la compile y la inyecte de forma limpia:

Bash

```
yay -S nvidia-580xx-dkms nvidia-580xx-utils lib32-nvidia-580xx-utils
```

> ⚠️ **Nota:** Durante la instalación, `yay` te va a avisar que estos paquetes entran en conflicto con `nouveau`. Dile que **SÍ** deseas reemplazarlos y eliminar `nouveau`. Es justo lo que queremos.

### Paso 3: Asegurar el Early KMS (El arranque temprano)

Para que el sistema cargue este driver específico al encender, abre el archivo de configuración:

Bash

```
sudo nano /etc/mkinitcpio.conf
```

Asegúrate de que la línea de módulos tenga los parámetros de video:

Plaintext

```
MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)
```

Guarda (`Ctrl + O`) y sal (`Ctrl + X`).

### Paso 4: Reconstruir y Reiniciar

Aplica los cambios en el cargador de arranque y reinicia la máquina:

Bash

```
sudo mkinitcpio -P
sudo reboot
```

### ¿Por qué pasa esto? 🔍

El error te dice: `nvidia-580xx-utils: /usr/lib/gbm/nvidia-drm_gbm.so exists in filesystem`.

Lo que ocurre es que cuando el driver oficial antiguo (o algún residuo de los intentos anteriores) se desinstaló, dejó huérfano ese archivo suelto en el sistema. Como `pacman` es extremadamente protector con tu disco duro, ve que el nuevo driver `nvidia-580xx-utils` quiere escribir un archivo exactamente en esa misma ruta y, para no sobreescribir nada sin tu permiso, **cancela la instalación por seguridad**.

## La Solución: Forzar el reemplazo de los archivos rebeldes

Tenemos dos formas de solucionarlo. La más rápida y limpia es decirle a `yay` / `pacman` que ignore la protección solo para ese archivo en específico y lo pise sin miedo:

### Opción A (La más rápida)

Vuelve a lanzar la instalación pasándole el parámetro `--overwrite` para obligar a `pacman` a sobreescribir cualquier archivo conflictivo en esa ruta de librerías (`/usr/lib/*`):

Bash

```
yay -S nvidia-580xx-dkms nvidia-580xx-utils lib32-nvidia-580xx-utils --overwrite "/usr/lib/*"
```

### Opción B (Si la opción A te vuelve a dar problemas)

Si por alguna razón te salta otro archivo diferente en la lista de conflictos, simplemente bórralo a mano con permisos de administrador y relanza la instalación normal:

1. Borra el archivo conflictivo:
    
    Bash
    
    ```
    sudo rm /usr/lib/gbm/nvidia-drm_gbm.so
    ```
    
2. Vuelve a ejecutar la instalación limpia:
    
    Bash
    
    ```
    yay -S nvidia-580xx-dkms nvidia-580xx-utils lib32-nvidia-580xx-utils
    ```
## Purgar los Kernels viejos y liberar espacio

Vamos a borrar las imágenes del Kernel Zen o del Kernel normal que no estás usando para dejarle espacio libre exclusivo a tu nuevo sistema.

### Paso 1: Ver qué archivos están tragándose el espacio

Miremos qué hay dentro de la partición de arranque ejecuntado:

Bash

```
ls -lh /boot/
```

Verás archivos pesados como `initramfs-linux.img`, `initramfs-linux-zen.img`, etc. Cada par de archivos (Kernel + initramfs) se traga unos 50-100MB.

### Paso 2: Borrar manualmente las imágenes de los Kernels que NO vas a usar

Como vas a utilizar el Kernel normal o el LTS con tu nuevo driver `nvidia-580xx-dkms`, vamos a sacrificar las imágenes del Kernel Zen para liberar unos 150MB de golpe:

Bash

```
sudo rm -f /boot/initramfs-linux-zen*
sudo rm -f /boot/vmlinuz-linux-zen*
```

Si también tienes residuos de otros entornos viejos, bórralos (asegúrate de mantener al menos el tuyo, que según tu log es el `linux` normal o el `linux-lts`):

Bash

```
# Borrar respaldos viejos que ocupan el doble de espacio
sudo rm -f /boot/*-fallback.img
```

### Paso 3: Limpiar la caché de descargas de Pacman (Por si acaso)

A veces el espacio que se llena no es `/boot`, sino la raíz entera del sistema debido a los gigas de instaladores guardados. Ejecuta esto para vaciar la caché de paquetes antiguos:

Bash

```
sudo pacman -Scc
```

_(Dile que **SÍ** a todo para limpiar el disco)._

### Paso 4: Reintentar la compilación obligatoria (Para asegurar el arranque)

Ahora que ya recuperamos oxígeno en el disco, obliga al sistema a generar **únicamente** la imagen de tu Kernel activo (sin intentar generar la de Zen que borramos).

Si estás usando el Kernel normal, corre:

Bash

```
sudo mkinitcpio -p linux
```

_(Si estás usando el LTS, corre `sudo mkinitcpio -p linux-lts`)_.

### Paso 1: Ver cuánto mide exactamente tu EFI

Para confirmar las sospechas, ejecuta:

Bash

```
df -h /boot
```

Verás que el porcentaje de uso está rozando el **100%**.

### Paso 2: El truco de magia (Configurar XBOOTLDR con systemd-boot)

`systemd-boot` (tu cargador de arranque) soporta una especificación espectacular llamada **XBOOTLDR**. Nos permite montar la partición EFI en `/efi` (solo para el arranque básico) y usar `/boot` dentro de tu disco de 1TB para almacenar las imágenes pesadas.

Vamos a automatizar el cambio de compresión. En lugar de usar la compresión por defecto, le diremos a tu sistema que use **`xz`** o **`lz4`** con hilos avanzados, lo que reducirá el tamaño de tus `initramfs` pesados de 295MB a unos **60MB o 70MB** de golpe.

1. Abre el configurador de imágenes:
    
    Bash
    
    ```
    sudo nano /etc/mkinitcpio.conf
    ```
    
2. Baja hasta el puro final del archivo. Busca la línea que dice `#COMPRESSION="zstd"` o similar.
    
3. Descoméntala (quita el `#`) y cámbiala por **`xz`** (que es la que más comprime del planeta, ideal para particiones EFI pequeñas):
    
    Plaintext
    
    ```
    COMPRESSION="xz"
    ```
    
4. Si quieres máxima velocidad usando todos los núcleos de tu i7, puedes usar `zstd` pero ultra-comprimido cambiando los argumentos abajo:
    
    Plaintext
    
    ```
    COMPRESSION_OPTIONS=(-v -T0 --ultra -20)
    ```
    
    _(Cualquiera de las dos opciones derretirá el tamaño de los archivos)._
    
5. Guarda con `Ctrl + O` y sal con `Ctrl + X`.
    

### Paso 3: Borrar el Kernel Zen para abrir espacio inmediato de maniobra

Dado que estás usando el Kernel **Zen** y el **LTS**, y el Zen se quedó a medio compilar (pesa 165M en lugar de los ~290M reales), bórralo para liberar oxígeno en la EFI y poder terminar la instalación de tus drivers de Nvidia:

Bash

```
sudo rm -f /boot/initramfs-linux-zen.img
sudo rm -f /boot/vmlinuz-linux-zen
```

### Paso 4: Recompilar con la nueva compresión "Slim"

Ahora que liberamos esos 165MB borrando el Zen, ejecutemos la regeneración del Kernel LTS (o el normal que uses) usando el nuevo algoritmo ultra-comprimido:

Bash

```
sudo mkinitcpio -p linux-lts
```

Verás que esta vez **SÍ va a terminar con éxito** porque el archivo final resultante va a pesar una fracción de lo que pesaba antes, dándole espacio de sobra a tu GTX 1060 para inyectar sus módulos de video.

Cuando termine, corre `sudo bootctl update` y reinicia. ¡El disco de 1TB volverá a respirar!

verificacion

### 1. Comprobar que las imágenes se crearon completas

Vamos a ver cuánto pesan ahora tus archivos comprimidos en `/boot` con el truco que hicimos:

Bash

```
ls -lh /boot/
```

> **Qué debes buscar:** Deberías ver que `initramfs-linux-lts.img` ahora pesa muchísimo menos que los 295MB originales (probablemente bajó a 60MB - 90MB), confirmando que le dejamos un montón de aire libre a la partición.

### 2. Comprobar el espacio libre real

Miremos cuánta vida le queda a esa mini-partición para estar seguros de que no está al 99%:

Bash

```
df -h /boot
```

> **Qué debes buscar:** El porcentaje de uso (`Use%`) debería haber bajado drásticamente a un número cómodo (como 40% o 60%). Si es así, estamos blindados para futuras actualizaciones.

### 3. La prueba reina: ¿NVIDIA está viva?

Para comprobar si el Kernel ya cargó los módulos de la serie 580xx para tu GTX 1060, ejecuta nuestro viejo amigo:

Bash

```
nvidia-smi
```

> **Qué debes buscar:** Si te despliega la mítica tabla tabular con el nombre **"GeForce GTX 1060 6GB"**, el uso de memoria y la versión del driver fija en la rama 580.xx... **¡LO LOGRAMOS POR COMPLETO!**

Si esos tres checkmarks están en verde, ejecuta un glorioso:

Bash

```
sudo reboot
```