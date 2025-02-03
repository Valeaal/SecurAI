import joblib
import struct
import socket
import numpy as np
import tensorflow as tf
from scapy.layers.l2 import ARP, Ether
from tensorflow.keras.models import load_model  # type: ignore
from sklearn.preprocessing import StandardScaler

# Cargar modelo entrenado y escalador
model = load_model('./app/machineModels/models/arpSpoofing_flooding.h5')
scaler = joblib.load('./app/machineModels/models/arpSpoofing_flooding.pkl')

# Diccionarios globales para el conteo de paquetes por MAC en tiempo real
arp_counts = {}  
arp_request_counts = {}  
arp_reply_counts = {}  

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

        # Inicializar contadores si la MAC no existe
        if src_mac_arp not in arp_counts:
            arp_counts[src_mac_arp] = 0
            arp_request_counts[src_mac_arp] = 0
            arp_reply_counts[src_mac_arp] = 0

        # Actualizar conteo de paquetes ARP
        arp_counts[src_mac_arp] += 1

        # Actualizar conteo de requests/replies
        if op_code == 1:
            arp_request_counts[src_mac_arp] += 1
        elif op_code == 2:
            arp_reply_counts[src_mac_arp] += 1

        # Calcular el ratio de requests/replies (para evitar división por 0 se suma 1)
        ratio_request_reply = arp_request_counts[src_mac_arp] / (arp_reply_counts[src_mac_arp] + 1)

        # Crear la lista de características (sin incluir direcciones MAC ni protocol)
        features = np.array([
            int(src_mac_eth != src_mac_arp), # mac_diferente_eth_arp
            arp_counts[src_mac_arp],         # arp_packets_por_mac
            arp_request_counts[src_mac_arp],   # arp_request_count
            arp_reply_counts[src_mac_arp],     # arp_reply_count
            ratio_request_reply,             # ratio_request_reply
            op_code                          # op_code(arp)
        ]).reshape(1, -1)

        return features
    else:
        return None

# Función de detección
def detect(packet):
    features = extract_features(packet)

    if features is not None:
        # Imprimir las características calculadas para el paquete
        print("Características del paquete ARP:", features)

        # Escalar características
        features_scaled = scaler.transform(features)

        # Hacer la predicción con la red neuronal
        prediction = model.predict(features_scaled)

        # Interpretar el resultado
        if prediction[0] > 0.8:
            print("🚨 ¡Alerta: Ataque ARP Flooding detectado! Probabilidad:", prediction[0])
            return "Attack: ARP Flooding"
        else:
            print("✅ ARP normal. Probabilidad:", prediction[0])
            return "No Attack"
    else:
        return "Not an ARP Packet"
