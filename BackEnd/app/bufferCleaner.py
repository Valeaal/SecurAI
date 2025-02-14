import time
from scapy.all import ARP, scapy 
from .packetCapture import packetBuffer

def bufferCleaner():
    while True:
        time.sleep(15)

        with packetBuffer.mutex:
            print(f"🗑️ Limpiando el buffer manteniendo el orden")

            original_list = list(packetBuffer.queue)
            new_list = []
            
            for indexed_packet in original_list:
                if indexed_packet.is_fully_processed():
                    continue
                else:
                    new_list.append(indexed_packet)
            
            # Limpiamos la cola interna y reinsertamos los paquetes en el mismo orden
            packetBuffer.queue.clear()
            for item in new_list:
                packetBuffer.queue.append(item)
