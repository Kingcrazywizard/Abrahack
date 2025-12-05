# Infraestructura y configuración avanzada de instancia EC2 personalizada

proyecto: RedPrivadaAnonimaAWS
descripcion: |
  Instancia EC2 configurada con doble VPN (WireGuard), proxy Tor, Privoxy, redirección de tráfico,
  DNS cifrado con DNSCrypt, gestión por scripts, acceso con alias SSH, automatizaciones con n8n
  y arquitectura modular para albergar futuros servicios como email server, DNS hosting o dominio onion.

version: 1.0
ultima_actualizacion: 2025-04-19
autor: Avrahka & IA

instancia:
  sistema_operativo: Ubuntu 24.04
  tipo: t2.micro
  almacenamiento: 12 GiB
  acceso:
    ssh:
      puerto: 4422
      alias: xxxx
      clave_ssh: xxxx_xxxx.pem
    vpn:
      wg0: tráfico general
      wg1: tráfico anónimo vía Tor
  seguridad:
    iptables:
      - cadena: REDSOCKS
        reglas: 
        [sudo iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
        sudo iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN]
      - REDIRECT:
        reglas: 
        [sudo iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 14444]
      - INPUT:
        reglas: 
        [sudo iptables -A INPUT -p udp --dport 42069 -j ACCEPT
        sudo iptables -A INPUT -p udp --dport 53000 -j ACCEPT
        sudo iptables -A INPUT -i wg1 -p tcp --dport 8443 -j ACCEPT]
      - OUTPUT:
        reglas: 
        [sudo iptables -t nat -A OUTPUT -p tcp -j REDSOCKS
        sudo iptables -t nat -I OUTPUT -d 10.100.100.0/24 -j RETURN]
      - FORWARD:
        reglas:
        [sudo iptables -A FORWARD -i wg0 -o enX0 -j ACCEPT
        sudo iptables -A FORWARD -i eth0 -o wg0 -m state --state RELATED,ESTABLISHED -j ACCEPT
        sudo iptables -A FORWARD -i wg1 -o enX0 -j ACCEPT
        sudo iptables -A FORWARD -i enX0 -o wg1 -m state --state RELATED,ESTABLISHED -j ACCEPT
        sudo iptables -A FORWARD -i enX0 -o wg1 -m state --state RELATED,ESTABLISHED -j ACCEPT]
      - POSTROUTING:
        reglas:
        [sudo iptables -t nat -A POSTROUTING -s 10.100.100.0/24 -o enX0 -j MASQUERADE
        sudo iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o enX0 -j MASQUERADE] 
      - PREROUTING
       reglas:
       [sudo iptables -t nat -A PREROUTING -i wg1 -p udp --dport 53 -j REDIRECT --to-port 5353]
    sg_aws:
      - 4422/TCP acceso SSH restringido
      - 53000/UDP acceso WireGuard (wg1)
      - 42069/UDP acceso Wireguard (wg0)

servicios:
  proxy:
    tipo: Privoxy
    puerto: 8443
    conector: SOCKS5 :9050
  tor:
    puerto: 9050
    salida: red Tor
  dns:
    servidor: DNSCrypt Proxy
    puerto: 5353
    proveedor: Cloudflare (sin logs, con DNSSEC)
  vpn:
    servidor: WireGuard
    interfaces: [wg0, wg1]
    ip_ranges:
      - wg0: 10.100.100.0/24
      - wg1: 10.200.200.0/24
    uso:
      - wg0: acceso seguro desde dispositivos autorizados
      - wg1: tráfico anónimo y enrutable vía Tor
  automatizacion:
    herramienta: n8n (planificada)
    acceso: interno, desde VPN

mecanismo_anonimato:
  - acceso solo vía VPN
  - eliminación del puerto 8443 de SG
  - redirección de tráfico de wg1 vía redsocks a Tor
  - resolución DNS local cifrada con DNSCrypt

backups:
  - ami_personalizada: activa
  - snapshot: eliminado luego de uso

futuro:
  - host de DNS propio
  - servidor de correo con dominio propio
  - servicio onion
  - clúster de nodos replicables

documentacion_relacionada:
  - configuracion_vpn.md
  - configuracion_proxy.md
  - configuracion_dnscrypt.md
  - flujo_redireccionamiento.md
