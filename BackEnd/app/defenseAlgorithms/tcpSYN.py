import os
import time
import psutil
import joblib
import warnings
import numpy as np
from app import attackNotifier
from scapy.layers.inet import IP, TCP
from app.packetCapture import packetBuffer
from tensorflow.keras.models import load_model  # type: ignore
from collections import defaultdict

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False  # Variable global de control para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo entrenado y escalador
model = load_model('./app/machineModels/models/tcpSYN.h5')
scaler = joblib.load('./app/machineModels/models/tcpSYN.pkl')

# Diccionario global para mantener estadísticas por flujo
flow_stats = defaultdict(lambda: {
    'syn_count': 0,
    'ack_count': 0,
    'fwd_pkts': 0,
    'bwd_pkts': 0,
    'start_time': None,
    'last_time': None,
    'pkt_timestamps': [],  # Para calcular IAT
    'fwd_timestamps': [],  # Para IAT forward
})

def get_flow_key(packet):
    """Obtiene la clave única de un flujo basada en la tupla (Src IP, Dst IP, Src Port, Dst Port)."""
    if IP in packet and TCP in packet:
        ip_layer = packet[IP]
        tcp_layer = packet[TCP]
        return (ip_layer.src, ip_layer.dst, tcp_layer.sport, tcp_layer.dport)
    return None

def extract_features(packet):
    from scapy.all import IP, TCP  # Asegúrate de importar esto
    
    if IP in packet and TCP in packet:
        ip_layer = packet[IP]
        tcp_layer = packet[TCP]
        flow_key = get_flow_key(packet)
        if not flow_key:
            return None

        flow = flow_stats[flow_key]
        current_time = time.time()

        # Inicializar el flujo si es nuevo
        if flow['start_time'] is None:
            flow['start_time'] = current_time
        flow['last_time'] = current_time

        # Determinar dirección del paquete
        direction = 'fwd' if ip_layer.src == flow_key[0] else 'bwd'
        if direction == 'fwd':
            flow['fwd_pkts'] += 1
            flow['fwd_timestamps'].append(current_time)
        else:
            flow['bwd_pkts'] += 1
        flow['pkt_timestamps'].append(current_time)

        # Contar flags
        if 'S' in tcp_layer.flags:
            flow['syn_count'] += 1
        if 'A' in tcp_layer.flags:
            flow['ack_count'] += 1

        # Calcular características
        flow_duration = (flow['last_time'] - flow['start_time']) * 1e6  # Microsegundos
        tot_pkts = flow['fwd_pkts'] + flow['bwd_pkts']
        flow_pkts_s = tot_pkts / (flow_duration / 1e6) if flow_duration > 0 else 0  # Paquetes por segundo
        fwd_pkts_s = flow['fwd_pkts'] / (flow_duration / 1e6) if flow_duration > 0 else 0  # Paquetes forward por segundo

        # Calcular IAT (tiempos entre llegadas)
        if len(flow['pkt_timestamps']) > 1:
            iat = np.diff(flow['pkt_timestamps'])
            flow_iat_mean = np.mean(iat) * 1e6  # Microsegundos
        else:
            flow_iat_mean = 0

        if len(flow['fwd_timestamps']) > 1:
            fwd_iat = np.diff(flow['fwd_timestamps'])
            fwd_iat_mean = np.mean(fwd_iat) * 1e6  # Microsegundos
        else:
            fwd_iat_mean = 0

        # Calcular Down/Up Ratio
        down_up_ratio = flow['bwd_pkts'] / (flow['fwd_pkts'] + 1e-6)  # Evitar división por cero

        # Crear array de características
        features = np.array([
            flow['syn_count'],      # SYN Flag Cnt
            flow['ack_count'],      # ACK Flag Cnt
            flow['fwd_pkts'],       # Tot Fwd Pkts
            flow['bwd_pkts'],       # Tot Bwd Pkts
            flow_duration,          # Flow Duration
            flow_pkts_s,            # Flow Pkts/s
            fwd_pkts_s,             # Fwd Pkts/s
            flow_iat_mean,          # Flow IAT Mean
            fwd_iat_mean,           # Fwd IAT Mean
            down_up_ratio           # Down/Up Ratio
        ]).reshape(1, -1)

        return features
    return None

def detect():
    global running

    with packetBuffer.mutex:
        current_packet = packetBuffer.queue[0]
    while current_packet == None:
        time.sleep(0.5)
        try:
            with packetBuffer.mutex:
                current_packet = packetBuffer.queue[0]
        except:
            current_packet = None

    while True:
        packet = current_packet.packet  # Referencia al paquete actual

        if running and IP in packet and TCP in packet:
            features = extract_features(packet)
            if features is not None:
                
                feature_names = [
                    "SYN Flag Cnt",
                    "ACK Flag Cnt",
                    "Tot Fwd Pkts",
                    "Tot Bwd Pkts",
                    "Flow Duration",
                    "Flow Pkts/s",
                    "Fwd Pkts/s",
                    "Flow IAT Mean",
                    "Fwd IAT Mean",
                    "Down/Up Ratio"
                ]
                
                # Escala las características
                features_scaled = scaler.transform(features)
                # Predice
                prediction = model.predict(features_scaled, verbose=0)
                print(f"-----------------tcpSYN-----------------------")
                print("Características usadas para la predicción:")
                if prediction[0] > 0.5:
                    print(f"🚨 ¡Alerta TCP SYN Flooding! (Prob attk: {prediction[0][0]:.2%})")
                    attackNotifier.notifyAttack(ALGORITHM_NAME)
                else:
                    print(f"✅ Tráfico normal (Prob attk: {prediction[0][0]:.2%})")
                    
                for name, value in zip(feature_names, features[0]):
                    print(f"{name}: {value}")

        ### PROCESO DE ENLACE AL SIGUIENTE PAQUETE, SIEMPRE HAY QUE MARCAR COMO COMPLETADO ###
        with packetBuffer.mutex:
            current_index = packetBuffer.queue.index(current_packet)
            remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        while remaining_packets == 0:
            time.sleep(0.5)                
            with packetBuffer.mutex:
                current_index = packetBuffer.queue.index(current_packet)
                remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        next_packet = packetBuffer.queue[current_index + 1]
        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
