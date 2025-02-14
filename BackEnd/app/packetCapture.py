import queue
import threading
from scapy.all import sniff
from .loadDefenseAlgorithms import getDefenseAlgorithmNames

packetBuffer = queue.Queue()
defenseAlgorithmsNames = getDefenseAlgorithmNames()

def packetCapture():
    sniff(prn=lambda packet: packetBuffer.put(PacketIndexed(packet, defenseAlgorithmsNames)), store=False)

# Estructura de dato que almacena un paquete conjunto con los filtros que ya ha pasado o no
class PacketIndexed:
    def __init__(self, packet, defenseAlgorithms):
        self.packet = packet
        self.processed = {name: 0 for name in defenseAlgorithms}
        self.lock = threading.Lock()

    def mark_processed(self, filter_name):
        # Marca el filtro como procesado para este paquete
        with self.lock:
            self.processed[filter_name] = 1

    def is_fully_processed(self):
        # Verifica si el paquete ha sido procesado por todos los filtros
        with self.lock:
            return all(v == 1 for v in self.processed.values())
