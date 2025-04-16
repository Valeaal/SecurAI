import os
import time
import socket
import joblib
import warnings
import numpy as np
from app import attackNotifier
from scapy.all import IP, TCP, IPv6
from app.packetCapture import packetBuffer, packetBufferLock
from tensorflow.keras.models import load_model  # type: ignore
from collections import defaultdict, deque

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False  # Variable global para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo y escalador
model = load_model('./app/machineModels/models/reconnaissance.h5')
scaler = joblib.load('./app/machineModels/models/reconnaissance.pkl')

# Diccionario global para estadísticas por flujo
flow_stats = {}

# Estructuras para rastrear ct_dst_ltm y ct_src_dport_ltm
connection_tracker = defaultdict(lambda: deque())  # IP destino -> cola de timestamps
TIME_WINDOW = 60  # Ventana de tiempo en segundos

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
local_ip = get_local_ip()

def update_connection_tracker(dst_ip, timestamp, flow_key):
    """Actualiza el rastreo de conexiones al destino, contando flujos únicos"""
    while connection_tracker[dst_ip] and connection_tracker[dst_ip][0][1] < timestamp - TIME_WINDOW:
        connection_tracker[dst_ip].popleft()
    # Añadir nuevo flujo si no existe
    if not any(fk == flow_key for fk, _ in connection_tracker[dst_ip]):
        connection_tracker[dst_ip].append((flow_key, timestamp))
    # Contar flujos únicos
    current_flows = set(fk for fk, _ in connection_tracker[dst_ip])
    return len(current_flows)

class FlowStats:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.spkts = 0
        self.dpkts = 0
        self.sbytes = 0
        self.dbytes = 0
        self.sttl = None
        self.dttl = None
        self.sinpkt = []
        self.dinpkt = []
        self.ct_dst_ltm = 0
        self.ct_src_dport_ltm = 0
        self.last_packet_time = None

    def update(self, packet, is_forward):
        current_time = packet.time
        if self.start_time is None:
            self.start_time = current_time
        self.end_time = current_time

        if is_forward:
            self.spkts += 1
            if IP in packet:
                self.sbytes += len(packet[IP])
                self.sttl = packet[IP].ttl
            elif IPv6 in packet:
                self.sbytes += len(packet[IPv6])
                self.sttl = packet[IPv6].hlim
            if self.last_packet_time is not None:
                inter_time = current_time - self.last_packet_time
                self.sinpkt.append(inter_time)
        else:
            self.dpkts += 1
            if IP in packet:
                self.dbytes += len(packet[IP])
                self.dttl = packet[IP].ttl
            elif IPv6 in packet:
                self.dbytes += len(packet[IPv6])
                self.dttl = packet[IPv6].hlim
            if self.last_packet_time is not None:
                inter_time = current_time - self.last_packet_time
                self.dinpkt.append(inter_time)

        self.last_packet_time = current_time

    def get_features(self):
        dur = self.end_time - self.start_time if self.start_time and self.end_time else 0
        rate = (self.spkts + self.dpkts) / dur if dur > 0 else 0
        smean = self.sbytes / self.spkts if self.spkts > 0 else 0
        dmean = self.dbytes / self.dpkts if self.dpkts > 0 else 0
        sinpkt = np.mean(self.sinpkt) if self.sinpkt else 0
        dinpkt = np.mean(self.dinpkt) if self.dinpkt else 0

        features = [
            dur,
            self.spkts,
            self.dpkts,
            self.sbytes,
            self.dbytes,
            rate,
            self.sttl if self.sttl is not None else 0,
            self.dttl if self.dttl is not None else 0,
            sinpkt,
            dinpkt,
            smean,
            dmean,
            self.ct_dst_ltm,
        ]
        return features

def get_flow_key(packet):
    if IP in packet:
        ip_layer = packet[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
    elif IPv6 in packet:
        ip_layer = packet[IPv6]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
    else:
        return None

    if TCP in packet:
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    else:
        return None

    # Ordenar para flujo bidireccional
    if src_ip < dst_ip:
        return (src_ip, dst_ip, src_port, dst_port)
    else:
        return (dst_ip, src_ip, dst_port, src_port)

def extract_features(packet):
    flow_key = get_flow_key(packet)
    if flow_key is None:
        return None

    if flow_key not in flow_stats:
        flow_stats[flow_key] = FlowStats()

    if IP in packet:
        ip_layer = packet[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
    elif IPv6 in packet:
        ip_layer = packet[IPv6]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
    else:
        return None

    is_forward = (flow_key[0] == ip_layer.src and flow_key[2] == packet[TCP].sport)

    # Actualizar contadores globales
    if TCP in packet:
        flow_stats[flow_key].ct_dst_ltm = update_connection_tracker(dst_ip, packet.time, flow_key)

    flow_stats[flow_key].update(packet, is_forward)

    features = flow_stats[flow_key].get_features()
    return np.array([features])

def print_features(features):
    feature_names = [
        "dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "sttl", "dttl",
        "sinpkt", "dinpkt", "smean", "dmean", "ct_dst_ltm"
    ]
    print("Características del paquete:")
    for name, value in zip(feature_names, features[0]):
        print(f"  {name}: {value}")

def detect():
    global running

    with packetBufferLock:
        while len(packetBuffer) == 0:
            time.sleep(0.5)
        current_packet = packetBuffer[0]

    while True:
        packet = current_packet.packet
        if running:
            features = extract_features(packet)

            if features is not None and packet.haslayer(IP) and packet[IP].dst == local_ip and packet[IP].src == local_ip:

                features_scaled = scaler.transform(features)
                prediction = model.predict(features_scaled, verbose=0)
                prob_attack = prediction[0][0]

                print(f"----------------- {ALGORITHM_NAME} -----------------")
                if prob_attack > 0.5:
                    print(f"🚨 ¡Alerta reconnaissance! (Prob attk: {prob_attack:.2%})")
                    attackNotifier.notifyAttack(ALGORITHM_NAME)
                else:
                    print(f"✅ Tráfico normal (Prob attk: {prob_attack:.2%})")
                
                print_features(features)

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
            next_packet = packetBuffer[current_index + 1]

        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet