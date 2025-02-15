import time
import sys
from .packetCapture import packetBuffer

#len(packetBuffer.queue) porque si no dentro del mutex lo queremos volver a coger y tenemos deadlock. En otros metodos 
def bufferCleaner():

    while True:
        time.sleep(5)
        paquetesEliminados = 0
        print(f"🗑️ 🗑️ 🗑️ Limpiando el buffer, tam: {packetBuffer.qsize()}")
       
        while packetBuffer.qsize() > 0:
            with packetBuffer.mutex:
                first_packet = packetBuffer.queue[0]
            if first_packet.is_fully_processed():
                packetBuffer.get()
                paquetesEliminados += 1
                print(f"Filtros del eliminado: ", first_packet.processed)
            else:
                print(f"Total eliminados: {paquetesEliminados}")
                break

        if packetBuffer.qsize() == 0:
            print("El buffer quedó vacío tras la limpieza.")

        print(f"🗑️ 🗑️ 🗑️ Limpieza terminada.")
