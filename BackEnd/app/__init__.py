import threading
import time
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

    spoofing_thread = threading.Thread(target=arpSpoofing)
    spoofing_thread.daemon = True
    spoofing_thread.start()

    return app

def arpSpoofing():

    target_ip = "10.0.0.2"  # IP de la que queremos conocer la MAC
    iface = "en0"  # Interfaz de red (ajústala según tu sistema)

    # Crear la solicitud ARP
    arp_request = ARP(op=1, pdst=target_ip)

    # Crear el marco Ethernet con dirección de difusión (broadcast)
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff") / arp_request

    time.sleep(12)
    print("Iniciando ARP Spoofing...")
    while True:
        sendp(ether_frame, iface=iface, verbose=False)


