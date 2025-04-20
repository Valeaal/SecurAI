import os
import time
import joblib
import warnings
import numpy as np
from collections import deque
from app import attackNotifier
from scapy.all import IP, UDP, DNS
from app.packetCapture import packetBuffer, packetBufferLock
from tensorflow.keras.models import load_model  # type: ignore

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo y escalador
model = load_model('./app/machineModels/models/dnsAmplification.h5')
scaler = joblib.load('./app/machineModels/models/dnsAmplification.pkl')

# Ventana deslizante de los últimos 100 “flujos” (paquetes) para cómputo de ct_*
history = deque(maxlen=100)

# Nombres de las características (para logging)
feature_names = [
    'dbytes',            # bytes de respuesta
    'dpkts',             # paquetes de respuesta
    'ct_dst_ltm',        # conexiones al mismo destino en últimos 100
    'ct_src_dport_ltm',  # repeticiones de (origen, puerto destino)
    'ct_dst_src_ltm'     # repeticiones de (origen, destino)
]

def extract_features(packet):
    """
    Dado un paquete DNS (respuesta UDP), extrae las 5 características usadas por el modelo:
      - dbytes: tamaño en bytes del paquete
      - dpkts: número de paquetes (siempre 1)
      - ct_dst_ltm: nº de paquetes previos en history con mismo dstip
      - ct_src_dport_ltm: nº de previos con misma (srcip, dport)
      - ct_dst_src_ltm: nº de previos con misma (srcip, dstip)
    Añade el flujo a history y devuelve un array shape (1,5).
    """
    try:
        # 1. dbytes: longitud total del paquete (bytes)
        raw = bytes(packet)
        dbytes = len(raw)
        # 2. dpkts: siempre 1 paquete
        dpkts = 1

        # 3‑5. contamos en history
        src = packet[IP].src
        dst = packet[IP].dst
        dport = packet[UDP].sport if packet[UDP].sport != 53 else packet[UDP].dport

        ct_dst_ltm = sum(1 for (s, d, dp) in history if d == dst)
        ct_src_dport_ltm = sum(1 for (s, d, dp) in history if s == src and dp == dport)
        ct_dst_src_ltm = sum(1 for (s, d, dp) in history if s == src and d == dst)

        # Guardamos este “flujo” en history
        history.append((src, dst, dport))

        features = np.array([[dbytes, dpkts, ct_dst_ltm, ct_src_dport_ltm, ct_dst_src_ltm]])
        return features

    except Exception:
        return None

def detect():
    global running

    # Esperamos al primer paquete
    with packetBufferLock:
        while len(packetBuffer) == 0:
            time.sleep(0.5)
        current_packet = packetBuffer[0]

    while True:
        packet = current_packet.packet

        ####### ANÁLISIS ########
        if running and packet.haslayer(UDP) and packet.haslayer(DNS):
            # Solo respuestas DNS (sport=53) o solicitudes (dport=53).  
            udp = packet[UDP]
            if udp.sport == 53 or udp.dport == 53:
                features = extract_features(packet)
                if features is not None:
                    # Escalado y predicción
                    features_scaled = scaler.transform(features)
                    prob_attack = model.predict(features_scaled, verbose=0)[0][0]

                    print(f"----- {ALGORITHM_NAME} -----")
                    if prob_attack > 0.5:
                        print(f"🚨 ¡Alerta DNS Amplification! ({prob_attack:.2%})")
                        attackNotifier.notifyAttack(ALGORITHM_NAME)
                    else:
                        print(f"✅ Tráfico normal (P={prob_attack:.2%})")

                    for name, val in zip(feature_names, features[0]):
                        print(f"{name}: {val}")

        ####### AVANZAR EN EL BUFFER ########
        with packetBufferLock:
            idx = packetBuffer.index(current_packet)
            remaining = len(packetBuffer) - (idx + 1)

        while remaining == 0:
            time.sleep(0.5)
            with packetBufferLock:
                idx = packetBuffer.index(current_packet)
                remaining = len(packetBuffer) - (idx + 1)

        with packetBufferLock:
            idx = packetBuffer.index(current_packet)
            next_packet = packetBuffer[idx + 1]

        ####### MARCADO ########
        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
