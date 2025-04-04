# Tutorial: Configurar un Proxy en AWS EC2 + Tor

## 1. Creación de la Instancia EC2 en AWS

### Inicia sesión en AWS:

- AWS Console.

### Dirígete a EC2:

- Busca "EC2" en la barra de búsqueda de servicios.

### Lanza una instancia:

- Haz clic en "Launch Instance".
- **Nombre:** Ponle un nombre como `Proxy-Tor-Server`.
- **AMI:** Selecciona `Amazon Linux 2`, `Ubuntu 20.04` o superior.
- **Tipo de instancia:** `t2.micro` (gratis con el nivel gratuito).
- **Almacenamiento:** `30 GB` (gratis con el nivel gratuito).

### Security Group (firewall):

- Permitir puertos:
  - `22 (SSH)` para acceso remoto.
  - `9050 (SOCKS5)` para Tor.
  - `8118 (HTTP/HTTPS)` si decides usar Privoxy.
- Añadir tu IP pública para mayor seguridad o dejar en `0.0.0.0/0` para acceso desde cualquier parte.
- **Par de claves:** Crea o usa un par de claves para SSH. Descárgalo y guárdalo en un lugar seguro.
- Haz clic en "Launch Instance".

---

## 2. Configuración del Servidor (EC2)

### Accede por SSH a tu instancia:

```bash
ssh -i /ruta/a/tu/clave.pem ubuntu@IP_PÚBLICA
```

Reemplaza `IP_PÚBLICA` con la IP de tu instancia y la ruta de tu clave privada.

### Actualiza el sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 3. Instalación de Tor y Privoxy

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

### (Opcional) Instala Privoxy (para navegación HTTP/HTTPS):

```bash
sudo apt install privoxy -y
```

### Edita su configuración:

```bash
sudo nano /etc/privoxy/config
```

Añade o edita:

```bash
listen-address 0.0.0.0:8118
forward-socks5t / 127.0.0.1:9050 .
```

### Reinicia Privoxy:

```bash
sudo systemctl restart privoxy
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

