import os
import time
import psutil
import joblib
import warnings
import numpy as np
from app import attackNotifier
from app.packetCapture import packetBuffer
from tensorflow.keras.models import load_model  # type: ignore

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False  # Variable global de control para detener el algoritmo

warnings.simplefilter("ignore", category=UserWarning)

# Cargar modelo entrenado y escalador
model = load_model('./app/machineModels/models/tcpSYN.h5')
scaler = joblib.load('./app/machineModels/models/tcpSYN.pkl')
    
your_interface = 'en0'  # Reemplaza con el nombre real de tu interfaz

def detect():
    global running
    last_prediction_time = time.time()
    last_stats = psutil.net_io_counters(pernic=True)[your_interface]

    with packetBuffer.mutex:
        current_packet = packetBuffer.queue[0]
    while current_packet == None:
        time.sleep(0.5)
        try:
            with packetBuffer.mutex:
                current_packet = packetBuffer.queue[0]
        except:
            current_packet == None

    while True:
        if running:
            current_time = time.time()
            if current_time - last_prediction_time >= 5:
                current_stats = psutil.net_io_counters(pernic=True)[your_interface]
                # Calcula los deltas
                delta_received_packets = current_stats.packets_recv - last_stats.packets_recv
                delta_received_bytes = current_stats.bytes_recv - last_stats.bytes_recv
                delta_sent_packets = current_stats.packets_sent - last_stats.packets_sent
                delta_sent_bytes = current_stats.bytes_sent - last_stats.bytes_sent

                # Extrae las características como array (solo deltas)
                features = np.array([[delta_received_packets, delta_received_bytes, delta_sent_packets, delta_sent_bytes]])

                # Mostrar las características antes de la predicción
                print(f"Características para predicción: "
                      f"Delta Received Packets={delta_received_packets}, Delta Received Bytes={delta_received_bytes}, "
                      f"Delta Sent Packets={delta_sent_packets}, Delta Sent Bytes={delta_sent_bytes}")

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