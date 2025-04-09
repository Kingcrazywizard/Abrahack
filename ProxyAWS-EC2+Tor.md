# GUÍA: PROXY EN AWS EC2 + TOR
**Configura un proxy en la nube con el servicio EC2 de Amazon Cloud (AWS) y ciframiento mediante TOR, de manera profesional, escalable y GRATUITA!!**


## 1. Creación de la Instancia EC2 en AWS

### 1.1 Inicia sesión en AWS y dirígete a EC2

- AWS Console.
- Busca "EC2" en la barra de búsqueda de servicios.

### 1.2 Lanza una instancia:

- Haz clic en "Launch Instance".
- **Nombre:** Ponle un nombre como `Proxy-Tor-Server`.
- **AMI:** Selecciona `Amazon Linux 2`, `Ubuntu 20.04` o superior. (Usaremos @ubuntu24.04)
- **Tipo de instancia:** `t2.micro` (gratis con el nivel gratuito).
- **Almacenamiento:** `30 GB` (gratis con el nivel gratuito).
- **Par de claves:** Crea o usa un par de claves para SSH. Descárgalo y guárdalo en un lugar seguro.
- Haz clic en "Launch Instance".

### 1.3 Security Group (SG):
**Los Security Groups son como firewalls por defecto a nivel de instancia.**

- Reglas de Entrada:
**Las reglas de entrada (ingress) controlan quienes (IPs) y como (Protocols & Ports) pueden conectarse a una instancia**
 
  - `(SSH) :22 (defecto) IP_PÚBLICA/32` para acceso remoto 
  - `(TCP) :8118 IP_PÚBLICA/32` para HTTP/HTTPS para Privoxy.
<details>
<summary>IP_PÚBLICA/32</summary> 

  - La máscara /32 en una IP limita el acceso exclusivamente a una sola IP pública exacta.
  - Permite usar tu proxy desde diferentes dispositivos simultáneamente, si ambos están en la misma red local y comparten la misma IP pública. Porque desde la perspectiva del servidor EC2 (Security Group), ambos dispositivos están saliendo por la misma IP pública del router

**Es probable que tu ISP no te proporcione una IP_PUBLICA estatica por lo que podrias:**
 - Usar un DNS Dinámico DDNS
 - Crear un VPN entre tus dispositivos y la instancia
 - Hacer un script para actualizar automaticamente tu SG con AWS CLI

</details>

- Reglas de Salida: 
**Las reglas de salida (egress) controlan hacia dónde puede conectarse a una instancia.**

  - `(ALL) 0.0.0.0/0` Todo el trafico, todos los protocolos, todos los puertos
  - Permite que la instancia EC2 haga cualquier tipo de conexión hacia afuera (HTTP, HTTPS, DNS, Tor, etc.).
  - Es la más usada por simplicidad y no suele representar riesgo.
  - AWS automáticamente permite el tráfico de respuesta (return traffic) gracias a una característica llamada “stateful firewall”, que recuerda las conexiones iniciadas desde adentro y permite su respuesta sin necesidad de reglas especiales de entrada.
---

## 2. Configuración del Servidor (EC2)

### 2.1 Accede por SSH a tu instancia:

**Desde tu CMD o terminal favorita**

```bash
ssh -i /ruta/a/tu/clave.pem ubuntu@IP_PÚBLICA
```
Reemplaza `IP_PÚBLICA` con la IP de tu instancia y la ruta de tu clave privada.

Recibiras una advertencia de seguridad estandar de SSH verificando el acceso de una nueva identidad al servidor. confirma con (yes)
```bash
The authenticity of host 'xx.xxx.xx.xxx (xx.xxx.xx.xxx)' can't be established. 
ED25519 key fingerprint is SHA256:......... 
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])?)
```
**(Puede que debas volver a validar tu acceso por SSH)**

### Actualiza el sistema:
```bash
sudo apt update && sudo apt upgrade -y
```
**(Verifica si debes hacer un reboot o solo haz reboot)**

```bash
[ -f /var/run/reboot-required ] && echo "⚠️ Reboot required"
```
```bash
sudo reboot
```

### (WSL INSTALL) 
A partir de aqui se recomienda utilizar WSL + @Ubuntu-24.04 

<details>
<summary>GUIA DE INSTALACIÓN, EN CASO DE QUE NO LO TENGAS</summary>

**este metodo instala Ubuntu por defecto**
```bash
wsl --install
```
Así Listas las distribuciones disponibles
```bash
wsl --list --online
## Instalamos -d de nuestra preferencia
wsl --install -d Ubuntu-24.04
```
Reboot 
```bash
shutdown.exe /r
```
Lista las distribuciones disponibles
```bash
wsl --list --online
```
Establecer WSL 2 como versión por defecto:
```bash
wsl --set-default-version 2
```
Cambiá los permisos del .pem
AWS requiere que el archivo .pem tenga permisos seguros. Ejecutá esto desde WSL:
```bash
chmod 400 /mnt/c/Users/TuUsuario/Descargas/mi-clave.pem
```
Ejecuta tu Instancia desde tu consola WSL ubuntu@
```bash
ssh -i /mnt/c/Users/TU_USUARIO/X/tu-clave.pem ubuntu@IPv4_Instancia
```
</details>

## 3. Instalación de Tor 

```bash
sudo apt install tor -y
```

### Edita el archivo de configuración de Tor:

```bash
sudo nano /etc/tor/torrc
```

Añade estas líneas al final para activar el proxy SOCKS5:

```bash
SocksPort 127.0.0.1:9050
ControlPort 9051
CookieAuthentication 1
```
Esto asegura que solo servicios locales (como Privoxy) puedan conectarse al servicio Tor.

Guarda y cierra.

### Reinicia Tor:

```bash
sudo systemctl restart tor
```

## 4. Instala Privoxy (para navegación HTTP/HTTPS):

```bash
sudo apt install privoxy -y
```

### Edita su configuración:
```bash
sudo nano /etc/privoxy/config
```

Añade en el lugar que prefieras del archivo /config omitiendo cualquier # al principio  

```bash
listen-address 0.0.0.0:8118
forward-socks5t / 127.0.0.1:9050 .
```
(Revisa el arhivo completo ya que privoxy tiene configuradas listen-address 127.0.0.1:8118 by default  
por lo que debes borrarlas o comentarlas con #)

Presiona Ctrl + O → y luego Enter (para guardar)
Luego Ctrl + X (para salir del editor).

### Reinicia Privoxy:

```bash
sudo systemctl restart privoxy
```
---

## 5. Comprueba la instalación:
Verificar si el proxy está corriendo (en la instancia)

```bash
sudo systemctl status tor
sudo systemctl status privoxy
```
Prueba en tu consola si Privoxy enruta correctamente el tráfico a Tor (SOCKS5)
(Usa la IP de tu EC2)
```bash
curl --proxy http://IP_PÚBLICA:8118 https://check.torproject.org/
```
```bash
Congratulations. This browser is configured to use Tor.
```

---

## ERRORES EN LA INSTALACIÓN?
<details>
<summary>REINSTALACIÓN</summary>

Desinstalar Tor y Privoxy por completo
```bash
sudo systemctl stop tor
sudo systemctl stop privoxy

sudo apt purge --autoremove tor privoxy
sudo rm -rf /etc/tor /var/lib/tor ~/.tor
sudo rm -rf /etc/privoxy /var/lib/privoxy
```
Verifica que no queda nada escuchando en el puerto 9050 o 8118
```bash
sudo lsof -i :9050
sudo lsof -i :8118
```
Si aún hay algo escuchando, reinicia la máquina para liberar completamente esos puertos:
sudo reboot
```bash
sudo reboot
```
</details>

---

## FELICITACIONES!!!
**AHORA CUENTAS CON UN RECURSO DE GRAN PODER PARA PROTEGER TU ANONIMATO Y PRIVACIDAD!! Y ESTE ES SOLO EL COMIENZO!!**
**CONFIGURAREMOS NUEVAS INTEGRACIONES PARA APROVECHAR EL MAYOR POTENCIAL DE NUESTRO SERVIDOR**
**...PERO ANTES ALGUNOS CONSEJOS ADICIONALES:**

## Crea un alias para establecer tu conexion SSH 
 
 ### Abre tu archivo de configuración de terminal
 ```bash
nano ~/.bashrc
 ```
 ### Agrega tu linea de comando al final del archivo
 ```bash
alias tu-alias='ssh -i ~/ruta/a/mi-clave.pem ubuntu@xx.xx.xx.xx'
 ```
 ### Haz reload a la configuración
 ```bash
 source ~/.bashrc
```
**Ya puedes usar tu alias cada vez que quieras ingresar a tu instancia**

---

## Mejora tu seguridad 

<details>

### <summary>Cambia el puerto de `(SSH) :22`</summary>

Edita el archivo de configuración de SSH
```bash
sudo nano /etc/ssh/sshd_config
```
Agregá/modificá estas líneas con el puerto de tu preferencia:
```bash
Port 4422
PermitRootLogin prohibit-password
PasswordAuthentication no
```
Manten el puerto 22 habilitado mientras haces pruebas
Revisa la sintaxis del archivo 
```bash
sudo sshd -t
```
Reiniciá el servicio SSH
```bash
sudo systemctl restart ssh
```
Verifica si el puerto esta escuchando
```bash
sudo ss -tuln | grep 4422
```
Deberias ver esto
```bash
LISTEN 0 128 0.0.0.0:4422 0.0.0.0:*
```
**Cambia la el ingress del SG (no elimines el puerto 22 hasta lograr acceder por tu nuevo puerto)**
- `(TCP) :4422 IP_PÚBLICA` 

Si no ha habido algun error, vuelve a ejecutar tu instancia desde tu consola de comandos usando el nuevo puerto
```bash
ssh -i /ruta/a/tu/archivo.pem -p 4422 usuario@ip-publica
```
Si no funciona puede que el directorio donde el servicio SSH guarda su PID o hace operaciones temporales no exista, 
entonces debamos crearlo
```bash
sudo mkdir -p /run/sshd
sudo chown root:sys /run/sshd
sudo chmod 755 /run/sshd
```
Revisa la sintaxis del archivo, verifica si el puerto escucha, reinicia el servicio SSH y prueba ejecutar la instancia de nuevo.
Si se a ejecutado sin problemas asume el riesgo y elimina el tu puerto `(SSH :22)` de tu SG
No olvides cambiar tu alias con la nueva linea SSH

### <summary>Cambia el puerto de `(HTTP/HTTPS) :8118`</summary>

Privoxy no tiene permisos para puertos menores a 1024, necesitaria ejecutarse como root 
O solo escoge uno mas alto.

Verifica que no haya ningún servicio en el puerto de tu elección
```bash
sudo ss -tuln | grep :443
```

Edita el archivo de configuración de Privoxy y cambia el puerto de escucha
```bash
listen-address  0.0.0.0:xxxx
```

Reinicia el servicio
```bash
sudo systemctl restart privoxy
```
Realiza pruebas de status en tus servicios
Crea la nueva regla en tu SG y elimina la anterior.
Verifica que tu trafico HTTP/HTTPS sea redirigido por Tor

</details>

- Instala un certificado SSL con Let's Encrypt si deseas mayor seguridad.

- Usa autenticación de clave pública para SSH en lugar de contraseñas.

---

## 7. Costos Estimados

Si te mantienes en el nivel gratuito con `t2.micro` y usas menos de `1GB` de salida al mes, debería ser gratuito. Si superas eso, el costo será bajo, unos `$5` al mes aproximadamente.

