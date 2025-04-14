import time
from .packetCapture import packetBuffer, packetBufferLock
from .loadDefenseAlgorithms import getDefenseAlgorithmNames

def bufferCleaner():
    while True:
        time.sleep(10)
        paquetesEliminados = 0
        print(f"🗑️ 🗑️ 🗑️ 🗑️ 🗑️ Limpiando el buffer, tam: {len(packetBuffer)}")

        with packetBufferLock:
            while len(packetBuffer) > 0:
                first_packet = packetBuffer[0]

                # Obtenemos la lista de filtros activos
                filtrosRequeridos = getDefenseAlgorithmNames()

                # Comprobamos si el paquete ha sido procesado por todos los filtros activos
                if all(first_packet.processed.get(filtro, 0) == 1 for filtro in filtrosRequeridos):
                    packetBuffer.pop(0)
                    paquetesEliminados += 1
                    # print(f"Filtros del eliminado: ", first_packet.processed)
                else:
                    print(f"🗑️ Total eliminados: {paquetesEliminados}")
                    break

            if len(packetBuffer) == 0:
                print("El buffer quedó vacío tras la limpieza.")

        print(f"🗑️ 🗑️ 🗑️ 🗑️ 🗑️ Limpieza terminada.")
