# CONFIGURA UN PROXY EN AWS

### Configura un proxy en la nube con el servicio EC2 de Amazon Cloud (AWS) y ciframiento a traves de TOR de manera profesional, escalable y GRATUITA!! 

¿Cómo funciona?
Creas una instancia EC2 (preferiblemente Linux) en AWS.

Instalas y configuras tu proxy (Squid, Dante, Privoxy, etc.) en la instancia.

Permites conexiones a tu proxy desde cualquier IP o restringes el acceso por seguridad.

Ventajas:
Disponibilidad 24/7: Siempre accesible mientras la instancia esté encendida.

Velocidad y estabilidad: Amazon ofrece buena conectividad y uptime.

Escalabilidad: Puedes aumentar los recursos (CPU, RAM) si lo necesitas.

Ubicación geográfica: Puedes elegir la región de AWS que desees, para acceder a contenido restringido por país.

Desventajas:
Costo: Aunque existe un nivel gratuito, si consumes mucho ancho de banda o usas instancias poderosas, tendrás que pagar.

Privacidad: Aunque AWS no debería interferir con tu tráfico, usar servicios comerciales introduce un pequeño riesgo.

Ideal para:
Acceso constante a un proxy desde cualquier lugar, sin depender de tu PC.

Configuraciones avanzadas con múltiples dispositivos.



En AWS EC2: Instalas Tor y configuras un proxy (Privoxy o Dante) para enrutar tráfico a través de Tor.
1. Diferencia entre usar Privoxy vs Dante con Tor:
Privoxy + Tor: Proxy HTTP → transforma tráfico HTTP en SOCKS5 → útil para apps que no soportan SOCKS5 nativo.
Dante + Tor: Proxy SOCKS → más directo y eficiente para apps compatibles con SOCKS5 → más flexible para TCP.
Si tus clientes soportan SOCKS5, Dante es más directo. Si no, Privoxy te traduce HTTP a SOCKS.


Restricción de IPs: Configuras Security Groups para permitir solo tus IPs o usar autenticación con contraseña en el proxy.

PC: Configuras tu navegador o sistema para usar la IP del proxy con el puerto especificado.

Android: Usas apps como Orbot o proxydroid para enrutar tráfico al proxy de AWS.

Los costos en AWS dependen principalmente de los servicios que uses y su configuración. Aquí te doy un resumen para lo que deseas:

1. EC2 (Servidor Virtual)
Instancia Gratis: AWS ofrece el nivel gratuito por 12 meses con una instancia t2.micro o t3.micro (1 vCPU, 1GB RAM) bajo Linux o Windows.

Costo fuera del nivel gratuito: Desde $0.0058/hora (t2.micro en Linux), que es alrededor de $4.20 al mes si está encendido todo el tiempo.

Instancias más potentes: Van desde $10 hasta cientos de dólares mensuales, según las especificaciones.

2. Almacenamiento (EBS)
30 GB de almacenamiento SSD gratuito en el nivel gratuito.

Fuera del nivel gratuito: $0.10/GB al mes.

3. Tráfico de Red
Entrada: Gratis.

Salida: Gratis hasta 1 GB/mes; luego, alrededor de $0.09/GB. Esto puede subir rápido si tienes mucho tráfico.

4. IP Estática (Elastic IP)
Gratis mientras se usa.

Si la reservas sin usar: $0.005/hora (alrededor de $3.60 al mes).

5. Otros Servicios (Opcionales)
S3 (Almacenamiento de archivos): $0.023/GB/mes.

CloudFront (CDN): Desde $0.085/GB.

Route 53 (DNS): $0.50 por dominio al mes.

Ejemplo de Costos Básicos (EC2 con Proxy y Tor)
Si configuras una instancia t2.micro en Linux con 30 GB EBS y un tráfico de salida moderado (10 GB al mes):

EC2: Gratis o $4.20/mes.

EBS: Gratis si usas menos de 30 GB.

Tráfico de Red: ~$0.81 por 10 GB.

Elastic IP: Gratis si la usas siempre.

Total Aproximado: Entre $0 y $5 al mes si no excedes el nivel gratuito.

Ultraseguridad.

¿Qué significa /32 en tus reglas de seguridad?
La máscara /32 en una IP (por ejemplo: 130.250.228.189/32) limita el acceso exclusivamente a un solo dispositivo con esa IP pública exacta.

Si planeas conectarte desde distintos lugares o redes, te conviene usar:

Una IP elástica de AWS para tu cliente (si es otra instancia).

O una IP dinámica, y actualizar el Security Group desde una app/script si cambia.

Privoxy escucha en 8118 para recibir peticiones entrantes.

Pero desde tu instancia puede salir por cualquier puerto, no necesita una regla para 8118 en salida salvo que estés haciendo peticiones desde el proxy hacia otro proxy en ese puerto específico.