import os
import time
import joblib
import warnings
import numpy as np
from app import attackNotifier
from scapy.layers.l2 import ARP, Ether
from app.packetCapture import packetBuffer
from tensorflow.keras.models import load_model  # type: ignore

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False  # Variable global de control para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# ── Cargar modelo entrenado y escalador (nuevos archivos) ───────────
model = load_model('./app/machineModels/models/arpFloodingSW.h5')
scaler = joblib.load('./app/machineModels/models/arpFloodingSW.pkl')

# Lista global para almacenar los paquetes ARP en la ventana deslizante (últimos 2 minutos)
# Cada entrada es un diccionario con las claves: 'time', 'src_mac', 'op_code', 'dst_ip'
arp_window = []

def mac_to_int(mac):
    return int(mac.replace(":", ""), 16) if isinstance(mac, str) else 0

def extract_features(packet):
    if packet.haslayer(ARP) and packet.haslayer(Ether):
        arp_layer = packet[ARP]
        ether_layer = packet[Ether]

        src_mac_arp = mac_to_int(arp_layer.hwsrc)
        src_mac_eth = mac_to_int(ether_layer.src)
        op_code = arp_layer.op  # 1 = Request, 2 = Reply
        dst_ip = arp_layer.pdst if op_code == 1 else "0.0.0.0"

        current_time = packet.time

        # ── Actualizar la ventana deslizante: eliminar paquetes antiguos ──
        while arp_window and arp_window[0]['time'] < current_time - 90:
            arp_window.pop(0)
        
        # Agregar la información del paquete actual a la ventana
        arp_window.append({
            'time': current_time,
            'src_mac': src_mac_arp,
            'op_code': op_code,
            'dst_ip': dst_ip if op_code == 1 else None
        })

        # Conteo total de paquetes en la ventana (global)
        sliding_count = len(arp_window)

        # ── Filtrar la ventana para obtener solo los paquetes de la misma MAC ──
        current_mac_window = [pkt for pkt in arp_window if pkt['src_mac'] == src_mac_arp]

        arp_packets_por_mac = len(current_mac_window)
        arp_request_count = sum(1 for pkt in current_mac_window if pkt['op_code'] == 1)
        arp_reply_count = sum(1 for pkt in current_mac_window if pkt['op_code'] == 2)
        ratio_request_reply = arp_request_count / (arp_reply_count + 1e-6)
        unique_ips = {pkt['dst_ip'] for pkt in current_mac_window if pkt['op_code'] == 1 and pkt['dst_ip'] not in (None, "", "0.0.0.0")}
        unique_ip_count = len(unique_ips)

        # Crear vector de características (8 columnas)
        features = np.array([
            op_code,                           # op_code(arp)
            int(src_mac_eth != src_mac_arp),   # mac_diferente_eth_arp
            arp_packets_por_mac,               # arp_packets_por_mac (en ventana)
            arp_request_count,                 # arp_request_count (en ventana)
            arp_reply_count,                   # arp_reply_count (en ventana)
            ratio_request_reply,               # ratio_request_reply (en ventana)
            unique_ip_count,                   # unique_dst_ip_count (en ventana)
            sliding_count                      # arp_count_sliding_window (total en ventana)
        ]).reshape(1, -1)
        
        return features
    else:
        return None

def detect():
    global running

    with packetBuffer.mutex:
        current_packet = packetBuffer.queue[0]
    while current_packet is None:
        time.sleep(0.5)
        try:
            with packetBuffer.mutex:
                current_packet = packetBuffer.queue[0]
        except:
            current_packet = None
            
    while True:
        packet = current_packet.packet  # Referencia al paquete actual

        ### PROCESO DE ANÁLISIS ###
        if running and packet.haslayer(ARP):
            features = extract_features(packet)
            print(f"-----------------arpFloodingSW-----------------------")
            if packet.haslayer(ARP) and packet[ARP].op == 1:
                print(f"ARP Request: Busca la IP {packet[ARP].pdst}")
            if packet.haslayer(ARP) and packet[ARP].op == 2:
                print(f"ARP Reply: La IP {packet[ARP].psrc} es {packet[ARP].hwsrc}")

            # Escalar características y hacer la predicción
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled, verbose=0)

            if prediction[0] > 0.5:
                print(f"🚨 ¡Alerta ARP Flooding! (Prob attk: {prediction[0][0]:.2%})")
                attackNotifier.notifyAttack(ALGORITHM_NAME)
            else:
                print(f"✅ Tráfico normal (Prob attk: {prediction[0][0]:.2%})")

        ### PROCESO DE ENLACE AL SIGUIENTE PAQUETE ###
        with packetBuffer.mutex:
            current_index = packetBuffer.queue.index(current_packet)
            remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        while remaining_packets == 0:
            time.sleep(0.5)
            with packetBuffer.mutex:
                current_index = packetBuffer.queue.index(current_packet)
                remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        next_packet = packetBuffer.queue[current_index + 1]

        # Marcar el paquete actual como procesado y avanzar
        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
