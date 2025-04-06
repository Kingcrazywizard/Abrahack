# Guía: Proxy en AWS EC2 + Tor 
## Configura un proxy en la nube con el servicio EC2 de Amazon Cloud (AWS) y ciframiento mediante TOR, de manera profesional, escalable y GRATUITA!! 


## 1. Creación de la Instancia EC2 en AWS

### 1.1 Inicia sesión en AWS y dirígete a EC2

- AWS Console.
- Busca "EC2" en la barra de búsqueda de servicios.

### 1.2 Lanza una instancia:

- Haz clic en "Launch Instance".
- **Nombre:** Ponle un nombre como `Proxy-Tor-Server`.
- **AMI:** Selecciona `Amazon Linux 2`, `Ubuntu 20.04` o superior.
- **Tipo de instancia:** `t2.micro` (gratis con el nivel gratuito).
- **Almacenamiento:** `30 GB` (gratis con el nivel gratuito).
- **Par de claves:** Crea o usa un par de claves para SSH. Descárgalo y guárdalo en un lugar seguro.
- Haz clic en "Launch Instance".

### 1.3 Security Group (firewall):
- **Los Security Groups son como firewalls por defecto a nivel de instancia.**

- Reglas de Entrada:
**Las reglas de entrada (ingress) controlan quienes (IPs) y como (Protocols & Ports) pueden conectarse a una instancia**
 
  - `(SSH) :22 (defecto)` para acceso remoto 
  - `(SOCKS5) :9050` para Tor.
  - `(HTTP/HTTPS) :8118` si decides usar Privoxy.
 
 - **IP_PÚBLICA/32** 
  - La máscara /32 en una IP limita el acceso exclusivamente a una sola IP pública exacta.
  - Permite usar tu proxy desde diferentes dispositivos simultáneamente, si ambos están en la misma red local y comparten la misma IP pública.
  Porque desde la perspectiva del servidor EC2 (Security Group), ambos dispositivos están saliendo por la misma IP pública del router

- Reglas de Salida:
**Las reglas de salida (egress) controlan hacia dónde puede conectarse a una instancia.**
 
 - `UDP (DNS) :53` 

-**0.0.0.0/0**
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
- Reemplaza `IP_PÚBLICA` con la IP de tu instancia y la ruta de tu clave privada.

- Recibiras una advertencia de seguridad estandar de SSH verificando el acceso de una nueva identidad al servidor. confirma con (yes)
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
**(Puede que debas hacer un reboot)**
puedes verificar con este comando:

```bash
[ -f /var/run/reboot-required ] && echo "⚠️ Reboot required"
```

### 2.2 Crea un alias para establecer tu conexion SSH (opcional)
---

## 3. Instalación de Privoy y Tor

### Instala Privoxy (para navegación HTTP/HTTPS):

```bash
sudo apt install privoxy -y
```

### Edita su configuración:

```bash
sudo nano /etc/privoxy/config
```

Añade o en el lugar que prefieras del archivo /config omitiendo cualquier # al principio
(Revisa el arhivo completo ya que privoxy tiene configuradas listen-address 127.0.0.1:8118 
by default por lo que debes borrarlas o comentarlas con #)

```bash
listen-address 0.0.0.0:8118
forward-socks5t / 127.0.0.1:9050 .
```
Presiona Ctrl + O → y luego Enter (para guardar)
Luego Ctrl + X (para salir del editor).
### Reinicia Privoxy:

```bash
sudo systemctl restart privoxy
```
### Instala Tor:

```bash
sudo apt install tor -y
```

### Edita el archivo de configuración de Tor:

```bash
sudo nano /etc/tor/torrc
```

Añade estas líneas al final para activar el proxy SOCKS5:

```bash
SocksPort 0.0.0.0:9050
ControlPort 9051
CookieAuthentication 1
```

Guarda y cierra.

### Reinicia Tor:

```bash
sudo systemctl restart tor
```
---

## 4. Configuración de Seguridad (Restricción de IPs)

- En AWS Console:
  - Ve a **Security Groups** de tu instancia.
  - Edita las reglas de entrada para permitir solo tu IP en los puertos `9050 (Tor)` y `8118 (Privoxy)`.

---

## 5. Configuración en Android y PC

### En Android:

- Instala **Orbot** o una app como **ProxyDroid**.
- Configura la app para usar la dirección IP de tu instancia EC2 y puerto `9050 (SOCKS5)` o `8118 (HTTP/HTTPS)`.
- Conéctate y verifica en sitios como [https://check.torproject.org/](https://check.torproject.org/) para comprobar que estás usando Tor.

### En PC:

- Configura tu navegador o sistema para usar un proxy SOCKS5:
  - **Dirección:** `IP_PÚBLICA`
  - **Puerto:** `9050`
- Puedes usar extensiones de navegador como **FoxyProxy** para gestionar tus conexiones.

---

## 6. Optimización y Seguridad (Opcional)

- Instala un certificado SSL con Let's Encrypt si deseas mayor seguridad.
- Cambia el puerto de SSH (`22`) a otro menos común para evitar ataques.
- Usa autenticación de clave pública para SSH en lugar de contraseñas.

---

## 7. Costos Estimados

Si te mantienes en el nivel gratuito con `t2.micro` y usas menos de `1GB` de salida al mes, debería ser gratuito. Si superas eso, el costo será bajo, unos `$5` al mes aproximadamente.

