from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, traceroute
from collections import defaultdict
import socket

# Lista para almacenar los paquetes capturados
paquetes = []

# Función que se llama cada vez que se captura un paquete
def capturar_paquete(paquete):
    paquetes.append(paquete)  # Agrega el paquete a la lista

# Captura de paquetes
print("Capturando paquetes durante 15 segundos... (Presiona Ctrl+C para detener)")
sniff(prn=capturar_paquete, timeout=15)  # Captura durante 15 segundos

# Diccionarios para el análisis
contar_protocolos = defaultdict(int)
contar_ips = defaultdict(int)
contar_tcp = defaultdict(int)
contar_udp = defaultdict(int)
contar_icmp = defaultdict(int)
intentos_por_ip = defaultdict(set)
contar_mac = defaultdict(int)
arp_tabla = {}
arp_spoofing_detectado = False
total_tamano = 0

# Procesar los paquetes para el análisis
for paquete in paquetes:
    # Obtener el protocolo
    if hasattr(paquete, 'lastlayer'):
        protocolo = paquete.lastlayer().name
        contar_protocolos[protocolo] += 1
    
    # Analizar TCP, UDP, ICMP (solo si el paquete tiene capa IP)
    if IP in paquete:
        if TCP in paquete:
            contar_tcp[paquete[IP].src] += 1
            if paquete[TCP].flags == "S":  # Bandera SYN para escaneo de puertos
                intentos_por_ip[paquete[IP].src].add(paquete[TCP].dport)
        elif UDP in paquete:
            contar_udp[paquete[IP].src] += 1
        elif ICMP in paquete:
            contar_icmp[paquete[IP].src] += 1
        
        # Obtener la dirección IP de destino
        ip_destino = paquete[IP].dst
        contar_ips[ip_destino] += 1

    # Analizar direcciones MAC (capa de enlace)
    if paquete.haslayer("Ether"):
        contar_mac[paquete["Ether"].src] += 1
        contar_mac[paquete["Ether"].dst] += 1

    # Detección de ARP Spoofing (solo si el paquete tiene capa ARP)
    if ARP in paquete and paquete[ARP].op == 2:  # ARP reply (is-at)
        ip = paquete[ARP].psrc
        mac = paquete[ARP].hwsrc
        if ip in arp_tabla and arp_tabla[ip] != mac:
            print(f"ARP Spoofing detectado: {ip} está ahora asociado a {mac}")
            arp_spoofing_detectado = True
        arp_tabla[ip] = mac
    
    # Sumar el tamaño del paquete
    total_tamano += len(paquete)

# Calcular tamaño promedio de los paquetes
tamano_promedio = total_tamano / len(paquetes) if paquetes else 0

# Encontrar la dirección IP más repetida
ip_mas_repetida = max(contar_ips, key=contar_ips.get, default=None)
ip_mas_repetida_contador = contar_ips.get(ip_mas_repetida, 0)

# Encontrar la dirección MAC más repetida
mac_mas_repetida = max(contar_mac, key=contar_mac.get, default=None)
mac_mas_repetida_contador = contar_mac.get(mac_mas_repetida, 0)

# Imprimir el análisis
print("\nResumen del análisis:")
print(f"Total de paquetes capturados: {len(paquetes)}")
print(f"Tamaño promedio de los paquetes: {tamano_promedio:.2f} bytes")

# Contador de paquetes por protocolo
print("\nContador de paquetes por protocolo:")
for protocolo, contador in contar_protocolos.items():
    print(f"{protocolo}: {contador}")

# Imprimir dirección IP más repetida
if ip_mas_repetida:
    print(f"\nDirección IP más repetida: {ip_mas_repetida} ({ip_mas_repetida_contador} veces)")

# Imprimir dirección MAC más repetida
if mac_mas_repetida:
    print(f"Dirección MAC más repetida: {mac_mas_repetida} ({mac_mas_repetida_contador} veces)")

# Lanzar traceroute a Google DNS (8.8.8.8)
print("\nIniciando traceroute al servidor 8.8.8.8 (Google DNS) para analizar la ruta de red.")

# Función para intentar resolver el nombre de dominio a partir de la IP
def resolver_nombre_ip(ip):
    try:
        return socket.gethostbyaddr(ip)[0]  # Devuelve el nombre de host
    except socket.herror:
        return None  # No se pudo resolver la IP

# Realizar el traceroute
res, no_res = traceroute("8.8.8.8")

# Procesar resultados del traceroute
print("\nResultados del traceroute:")
for snd, rcv in res:
    ip_origen = rcv.src
    rtt = (rcv.time - snd.sent_time) * 1000  # Calcular RTT en milisegundos
    
    # Intentar resolver el nombre de dominio
    nombre = resolver_nombre_ip(ip_origen)
    nombre_mostrado = f"({nombre})" if nombre else ""
    
    print(f"Salto: {ip_origen} {nombre_mostrado}, RTT: {rtt:.2f} ms")


# Detección de ARP Spoofing
if arp_spoofing_detectado:
    print("\nAlerta: Se detectó ARP Spoofing durante la captura.")
else:
    print("\nNo se detectó ARP Spoofing.")
