import time
import threading

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from .routes.loadDefenseAlgorithms import loadDefenseAlgorithms_bp


from .packetCapture import *
from .bufferCleaner import bufferCleaner
from .loadAttackTests import loadAttackTests
from .loadDefenseAlgorithms import loadDefenseAlgorithms

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, resources={r"/*": {"origins": "*"}})

def bufferMonitor():
    print(f"Emitiendo estado del buffer")
    while True:
        time.sleep(0.2)
        socketio.emit('buffer_status', {'size': packetBuffer.qsize()})
        #print(f"Emitiendo desde el socket: {packetBuffer.qsize()}")
        

def createApp():

    app.register_blueprint(loadDefenseAlgorithms_bp, url_prefix="/loadDefenseAlgorithms")

    # Hilo de captura de paquetes
    captureThread = threading.Thread(target=packetCapture, daemon=True)
    captureThread.start()

    # Cargar algoritmos de defensa
    loadDefenseAlgorithms()

    # Cargar algoritmos de ataque
    loadAttackTests()

    # Envio constante del estado del buffer al frontend
    bufferMonitorThread = threading.Thread(target=bufferMonitor, daemon=True)
    bufferMonitorThread.start()

    # Hilo de limpieza del buffer
    cleanerThread = threading.Thread(target=bufferCleaner, daemon=True)
    cleanerThread.start()

    return app