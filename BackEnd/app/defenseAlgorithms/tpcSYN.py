import os
import time
import psutil
import joblib
import warnings
import numpy as np
from app import attackNotifier
from tensorflow.keras.models import load_model  # type: ignore

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False # Variable global de control para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo entrenado y escalador
model = load_model('./app/machineModels/models/tcpSYN.h5')
scaler = joblib.load('./app/machineModels/models/tcpSYN.pkl')
    
your_interface = 'en0'  # Reemplaza con el nombre real de tu interfaz

def detect():
    global running
    last_prediction_time = time.time()
    last_stats = psutil.net_io_counters(pernic=True)[your_interface]
    while True:
        if running:
            current_time = time.time()
            if current_time - last_prediction_time >= 5:
                current_stats = psutil.net_io_counters(pernic=True)[your_interface]
                # Calcula las características
                received_packets = current_stats.packets_recv
                sent_packets = current_stats.packets_sent
                received_bytes = current_stats.bytes_recv
                sent_bytes = current_stats.bytes_sent
                # Calcula los deltas
                delta_received_packets = received_packets - last_stats.packets_recv
                delta_received_bytes = received_bytes - last_stats.bytes_recv
                delta_sent_packets = sent_packets - last_stats.packets_sent
                delta_sent_bytes = sent_bytes - last_stats.bytes_sent
                # Número de puerto (ya que solo tenemos uno)
                port_number = 1
                # Extrae las características como array
                features = np.array([[port_number, received_packets, sent_packets, received_bytes, sent_bytes,
                                      delta_received_packets, delta_received_bytes, delta_sent_packets, delta_sent_bytes
                                    ]])
                # Escala las características
                features_scaled = scaler.transform(features)
                # Predice
                prediction = model.predict(features_scaled, verbose=0)
                if prediction[0] > 0.5:
                    print(f"🚨 ¡Alerta TCP SYN Flooding! (Prob attk: {prediction[0][0]:.2%})")
                    attackNotifier.notifyAttack(ALGORITHM_NAME)
                else:
                    print(f"✅ Tráfico normal (Prob attk: {prediction[0][0]:.2%})")
                # Actualiza last_stats y last_prediction_time
                last_stats = current_stats
                last_prediction_time = current_time
        time.sleep(1)  # Verifica cada segundo