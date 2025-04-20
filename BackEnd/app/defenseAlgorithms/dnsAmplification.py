import os
import time
import warnings
from scapy.all import IP, UDP, DNS
from app import attackNotifier
from app.packetCapture import packetBuffer, packetBufferLock

ALGORITHM_NAME = os.path.basename(__file__).replace('.py', '')
running = False

warnings.simplefilter("ignore", category=UserWarning)

def detect():
    global running

    with packetBufferLock:
        while len(packetBuffer) == 0:
            time.sleep(0.5)
        current_packet = packetBuffer[0]

    while True:
        packet = current_packet.packet

        ####### ANÁLISIS ########
        if running and packet.haslayer(UDP) and packet.haslayer(DNS):
            udpLayer = packet[UDP]
            dnsLayer = packet[DNS]

            if udpLayer.sport == 53 or udpLayer.dport == 53:
                src = packet[IP].src
                dst = packet[IP].dst
                domain = dnsLayer.qd.qname.decode() if dnsLayer.qd else 'N/A'

                print(f"[DNS] {src} → {dst} | Dominio: {domain}")

        ####### AVANZAR EN EL BUFFER ########
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

        ####### MARCADO ########
        current_packet.mark_processed(ALGORITHM_NAME)
        current_packet = next_packet
