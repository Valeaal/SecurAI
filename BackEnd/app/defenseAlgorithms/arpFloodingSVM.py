import os
import time
import joblib
import warnings
import numpy as np
from app import attackNotifier
from scapy.layers.l2 import ARP, Ether
from app.packetCapture import packetBuffer, packetBufferLock


ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False # Variable global de control para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo entrenado y escalador
base_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio donde se encuentra el script

model_path = os.path.join(base_dir, '..', 'machineModels', 'models', 'arpFloodingSVMmodel.pkl')
scaler_path = os.path.join(base_dir, '..', 'machineModels', 'models', 'arpFloodingSVMscaler.pkl')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# Diccionarios globales para métricas en tiempo real
arp_counts = {}  
arp_request_counts = {}  
arp_reply_counts = {}  
unique_dst_ips = {}  # Para IPs destino únicas

def mac_to_int(mac):
    return int(mac.replace(":", ""), 16) if isinstance(mac, str) else 0

def extract_features(packet):
    if packet.haslayer(ARP) and packet.haslayer(Ether):
        arp_layer = packet[ARP]
        ether_layer = packet[Ether]

        src_mac_arp = mac_to_int(arp_layer.hwsrc)
        src_mac_eth = mac_to_int(ether_layer.src)
        op_code = arp_layer.op  # 1 = Request, 2 = Reply
        dst_ip = arp_layer.pdst if op_code == 1 else "0.0.0.0"  # Obtener IP destino

        # Inicializar contadores si la MAC no existe
        if src_mac_arp not in arp_counts:
            arp_counts[src_mac_arp] = 0
            arp_request_counts[src_mac_arp] = 0
            arp_reply_counts[src_mac_arp] = 0
            unique_dst_ips[src_mac_arp] = set()

        # Actualizar conteo de paquetes ARP
        arp_counts[src_mac_arp] += 1

        # Actualizar conteo de requests y conjunto de IPs únicas
        if op_code == 1:
            arp_request_counts[src_mac_arp] += 1
            if dst_ip not in ["0.0.0.0", "", None] and arp_layer.ptype == 0x0800:  # IPv4
                unique_dst_ips[src_mac_arp].add(dst_ip)
        elif op_code == 2:
            arp_reply_counts[src_mac_arp] += 1

        # Calcular métricas
        ratio_request_reply = arp_request_counts[src_mac_arp] / (arp_reply_counts[src_mac_arp] + 1e-6)
        unique_ip_count = len(unique_dst_ips[src_mac_arp])

        features = np.array([
            op_code,                           # op_code(arp)
            int(src_mac_eth != src_mac_arp),   # mac_diferente_eth_arp
            arp_counts[src_mac_arp],           # arp_packets_por_mac
            arp_request_counts[src_mac_arp],   # arp_request_count
            arp_reply_counts[src_mac_arp],     # arp_reply_count
            ratio_request_reply,               # ratio_request_reply
            unique_ip_count                    # unique_dst_ip_count
        ]).reshape(1, -1)

        return features
    else:
        return None
    
def detect():

    global running

###### OBTENCIÓN DEL PRIMER PAQUETE ######
    with packetBufferLock:
        num_packets = len(packetBuffer)
    
    while num_packets == 0:
        time.sleep(0.2)
        with packetBufferLock:
            num_packets = len(packetBuffer)          
    current_packet = packetBuffer[0]
    
    while True:
        packet = current_packet.packet

###### PROCESO DE ANALISIS ######
        if running and packet.haslayer(ARP):
            features = extract_features(packet)
            print(f"----------------arpFloodingSVM------------------------")
            # print("Características calculadas:", features[0])

            if packet.haslayer(ARP) and packet[ARP].op == 1:
                print(f"ARP Request: Busca la IP {packet[ARP].pdst}")
            if packet.haslayer(ARP) and packet[ARP].op == 2:
                print(f"ARP Reply: La IP {packet[ARP].psrc} es {packet[ARP].hwsrc}")

            # Escalar características y hacer la predicción
            features_scaled = scaler.transform(features)
            prediction = model.predict_proba(features_scaled)[0]  # [prob_normal, prob_ataque]

            # Umbral de detección (usamos prob_ataque, la segunda clase)
            if prediction[1] > 0.5:  # prediction[1] = probabilidad de ataque
                print(f"¡Alerta ARP Flooding! (Prob ataque: {prediction[1]:.2%})")
                attackNotifier.notifyAttack(ALGORITHM_NAME)
            else:
                print(f"Tráfico normal (Prob ataque: {prediction[1]:.2%})")

###### PROCESO DE ENLACE AL SIGUIENTE PAQUETE ######
        # Actualizamos siempre el indice del paquete actual, porque puede haberlo cambiado la hebra limpiadora.
        # Si hemos acabado con el buffer el último paquete no se marca como analizado para no perderlo y calcular luego el índice por el que va este proceso.

        with packetBufferLock:
            current_index = packetBuffer.index(current_packet)
            remaining_packets = len(packetBuffer) - (current_index + 1)
        
        while remaining_packets == 0:
            time.sleep(0.5)       
            with packetBufferLock:
                current_index = packetBuffer.index(current_packet)     
                remaining_packets = len(packetBuffer) - (current_index + 1)

        with packetBufferLock:
            current_index = packetBuffer.index(current_packet)
            remaining_packets = len(packetBuffer) - (current_index + 1)
            next_packet = packetBuffer[current_index + 1]

###### PROCESO DE MARCADO COMO ANALIZADO ######

        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
                
