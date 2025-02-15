import threading

from flask import Flask
from .routes.start import main_bp
from .routes.arpSpoofing import arpSpoofing_bp
from .bufferCleaner import bufferCleaner
from .packetCapture import packetCapture
from .loadAttackTests import loadAttackTests
from .loadDefenseAlgorithms import loadDefenseAlgorithms

def create_app():
    app = Flask(__name__)

    app.register_blueprint(main_bp)
    app.register_blueprint(arpSpoofing_bp)

    # Hilo de captura de paquetes
    captureThread = threading.Thread(target=packetCapture, daemon=True)
    captureThread.start()

    # Cargar algoritmos de defensa
    loadDefenseAlgorithms()

    # Cargar algoritmos de ataque
    loadAttackTests()

    # Hilo de limpieza del buffer
    cleanerThread = threading.Thread(target=bufferCleaner, daemon=True)
    cleanerThread.start()

    return app