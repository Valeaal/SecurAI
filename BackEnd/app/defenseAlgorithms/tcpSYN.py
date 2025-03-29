import os
import time
import psutil
import joblib
import warnings
import numpy as np
from app import attackNotifier
from scapy.all import IP, TCP, Ether, IPv6
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
# Se guardarán: flow_id, last_time y packet_count
flow_stats = {}

# Esta función obtiene la clave única de un flujo basado en la tupla (Src IP, Dst IP, Src Port, Dst Port)
def get_flow_key(packet):
    # Asegurar que el paquete tiene TCP
    if not TCP in packet:
        return None
    
    tcp = packet[TCP]
    src_port = tcp.sport
    dst_port = tcp.dport
    
    # Identificar IPv4/IPv6 y obtener direcciones
    if IP in packet:
        ip = packet[IP]
        version = 4
        src_ip = ip.src
        dst_ip = ip.dst
    elif IPv6 in packet:
        ip = packet[IPv6]
        version = 6
        src_ip = ip.src
        dst_ip = ip.dst
    
    # Crear clave única bidireccional (mismo ID para A->B y B->A)
    if src_ip < dst_ip:
        flow_key = (version, src_ip, dst_ip, src_port, dst_port)
    else:
        flow_key = (version, dst_ip, src_ip, dst_port, src_port)
    
    return flow_key

def extract_features(packet):
    """
    Extrae las características:
    - Flow ID: ID asignado al flujo.
    - Time Delta: Diferencia de tiempo respecto al último paquete del flujo.
    - FlagSYN, FlagURG, FlagACK, FlagPSH, FlagFIN, FlagRST: 1 si está presente, 0 si no.
    - packetCountInFlow: Conteo progresivo de paquetes en el flujo.
    """
    if IP not in packet or TCP not in packet:
        return None

    flow_key = get_flow_key(packet)
    if flow_key is None:
        return None

    # Considerar el flujo en ambas direcciones (tupla y su inversa)
    reverse_key = (flow_key[1], flow_key[0], flow_key[3], flow_key[2])
    if flow_key in flow_stats:
        stats = flow_stats[flow_key]
    elif reverse_key in flow_stats:
        stats = flow_stats[reverse_key]
        flow_key = reverse_key
    else:
        # Nuevo flujo: asignar un ID basado en la cantidad actual de flujos
        flow_id = len(flow_stats)
        stats = {
            'flow_id': flow_id,
            'last_time': None,
            'packet_count': 0,
        }
        flow_stats[flow_key] = stats

    # Calcular el delta de tiempo
    current_time = packet.time
    if stats['last_time'] is None:
        time_delta = 0.0
    else:
        time_delta = current_time - stats['last_time']
    stats['last_time'] = current_time

    # Incrementar el conteo de paquetes en el flujo
    stats['packet_count'] += 1

    # Extraer banderas del paquete TCP
    tcp_flags = packet[TCP].flags
    flag_syn = 1 if 'S' in tcp_flags else 0
    flag_urg = 1 if 'U' in tcp_flags else 0
    flag_ack = 1 if 'A' in tcp_flags else 0
    flag_psh = 1 if 'P' in tcp_flags else 0
    flag_fin = 1 if 'F' in tcp_flags else 0
    flag_rst = 1 if 'R' in tcp_flags else 0

    # Formar el vector de características (sin la etiqueta, pues se predice la probabilidad de ataque)
    features = np.array([[
        stats['flow_id'],
        time_delta,
        flag_syn,
        flag_urg,
        flag_ack,
        flag_psh,
        flag_fin,
        flag_rst,
        stats['packet_count']
    ]])
    return features

def detect():
    global running

    # Espera hasta que haya al menos un paquete en el buffer
    with packetBuffer.mutex:
        current_packet = packetBuffer.queue[0] if packetBuffer.queue else None
    while current_packet is None:
        time.sleep(0.5)
        with packetBuffer.mutex:
            current_packet = packetBuffer.queue[0] if packetBuffer.queue else None

    # Definir los nombres de las características para mostrar en el log (sin Flow ID)
    feature_names = [
        'Time Delta', 'FlagSYN', 'FlagURG',
        'FlagACK', 'FlagPSH', 'FlagFIN', 'FlagRST',
        'packetCountInFlow'
    ]

    while True:
        packet = current_packet.packet  # Referencia al paquete actual

        if running and IP in packet and TCP in packet:
            flow_key = get_flow_key(packet)  # Obtener Flow ID
            flow_id = flow_stats[flow_key]['flow_id'] if flow_key in flow_stats else "N/A"
            features = extract_features(packet)

            if features is not None:
                # Quitar el Flow ID de las características antes de escalar y predecir
                features_scaled = scaler.transform(features[:, 1:])
                # Realizar la predicción
                prediction = model.predict(features_scaled, verbose=0)
                prob_attack = prediction[0][0]

                print(f"----------------- {ALGORITHM_NAME} -----------------")                
                if prob_attack > 0.5:
                    print(f"🚨 ¡Alerta TCP SYN Flooding! (Prob attk: {prob_attack:.2%})")
                    attackNotifier.notifyAttack(ALGORITHM_NAME)
                else:
                    print(f"✅ Tráfico normal (Prob attk: {prob_attack:.2%})")

                # Mostrar cada característica y su valor (sin Flow ID)
                print(f"Flow ID: {flow_id} (no se usa)")
                for name, value in zip(feature_names, features[0][1:]):
                    print(f"{name}: {value}")

        # Proceso de pasar al siguiente paquete, siempre marcar el actual como procesado
        with packetBuffer.mutex:
            current_index = packetBuffer.queue.index(current_packet)
            remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        while remaining_packets == 0:
            time.sleep(0.5)
            with packetBuffer.mutex:
                current_index = packetBuffer.queue.index(current_packet)
                remaining_packets = len(packetBuffer.queue) - (current_index + 1)
        
        with packetBuffer.mutex:
            next_packet = packetBuffer.queue[current_index + 1]
        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
