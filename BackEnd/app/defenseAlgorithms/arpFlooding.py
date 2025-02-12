import joblib
import struct
import socket
import warnings
import numpy as np
import tensorflow as tf
from scapy.layers.l2 import ARP, Ether
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler

warnings.simplefilter("ignore", category=UserWarning)
# Cargar modelo entrenado y escalador
model = load_model('./app/machineModels/models/arpFlooding.h5')
scaler = joblib.load('./app/machineModels/models/arpFlooding.pkl')

# Diccionarios globales para métricas en tiempo real
arp_counts = {}  
arp_request_counts = {}  
arp_reply_counts = {}  
unique_dst_ips = {}  # Nuevo diccionario para IPs destino únicas

# Función para convertir direcciones MAC en enteros
def mac_to_int(mac):
    return int(mac.replace(":", ""), 16) if isinstance(mac, str) else 0

# Función para extraer características del paquete ARP
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
            unique_dst_ips[src_mac_arp] = set()  # Nuevo conjunto para IPs únicas

        # Actualizar conteo de paquetes ARP
        arp_counts[src_mac_arp] += 1

        # Actualizar conteo de requests y IPs únicas
        if op_code == 1:
            arp_request_counts[src_mac_arp] += 1
            # Filtrar IPs inválidas y añadir al conjunto
            if dst_ip not in ["0.0.0.0", "", None] and arp_layer.ptype == 0x0800:  # IPv4
                unique_dst_ips[src_mac_arp].add(dst_ip)
        elif op_code == 2:
            arp_reply_counts[src_mac_arp] += 1

        # Calcular métricas
        ratio_request_reply = arp_request_counts[src_mac_arp] / (arp_reply_counts[src_mac_arp] + 1e-6)
        unique_ip_count = len(unique_dst_ips[src_mac_arp])  # Nueva métrica

        # Crear la lista de características
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

# Función de detección
def detect(packet):
    features = extract_features(packet)

    if features is not None:
        print("----------------------------------------")
        print("Características calculadas:", features[0])  # Debug
        
        # Si es un ARP Request, mostrar la IP solicitada
        if packet.haslayer(ARP) and packet[ARP].op == 1:
            print(f"ARP Request: Busca la IP {packet[ARP].pdst}")

        # Escalar características
        features_scaled = scaler.transform(features)
        
        # Hacer predicción
        prediction = model.predict(features_scaled)
        
        # Umbral de detección
        if prediction[0] > 0.5:
            print(f"🚨 ¡Alerta ARP Flooding! (Prob: {prediction[0][0]:.2%})")
            print("----------------------------------------")
            return "Attack"
        else:
            print(f"✅ Tráfico normal (Prob: {prediction[0][0]:.2%})")
            print("----------------------------------------")
            return "No Attack"
    
    return "Not an ARP Packet"
