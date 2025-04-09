
# Configuración ProxyAWS+Tor en Android 

### Orbot

- Instala **Orbot** o una app como **ProxyDroid**.
- Configura la app para usar la dirección IP de tu instancia EC2 y puerto `9050 (SOCKS5)` o `8118 (HTTP/HTTPS)`.
- Conéctate y verifica en sitios como [https://check.torproject.org/](https://check.torproject.org/) para comprobar que estás usando Tor.

## 5. Configuración PC

### En PC:

- Configura tu navegador o sistema para usar un proxy SOCKS5:
  - **Dirección:** `IP_PÚBLICA`
  - **Puerto:** `9050`
- Puedes usar extensiones de navegador como **FoxyProxy** para gestionar tus conexiones.

---