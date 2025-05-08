import threading


from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from .packetCapture import *
from .loadDefenseAlgorithms import *
from .attackNotify import AttackNotifier
from .bufferMonitor import bufferMonitor
from .bufferCleaner import bufferCleaner
from .loadAttackTests import loadAttackTests

from .routes.loadAttackTests import loadAttackTests_bp
from .routes.loadDefenseAlgorithms import loadDefenseAlgorithms_bp

app = Flask(__name__)
global attackNotifier
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

base_dir = os.path.dirname(os.path.abspath(__file__))

CORS(app, resources={r"/*": {"origins": "*"}})

def createApp():

    app.register_blueprint(loadDefenseAlgorithms_bp, url_prefix="/loadDefenseAlgorithms")
    app.register_blueprint(loadAttackTests_bp, url_prefix="/loadAttackTests")

    # Creación del notificador de ataques al frontend, variable (objeto) global para todos los modulos
    global attackNotifier
    attackNotifier = AttackNotifier(socketio)

    # Hilo de captura de paquetes

    captureThread = threading.Thread(target=packetCapture, args=(socketio,), daemon=True)
    captureThread.start()

    # Cargar algoritmos de defensa
    loadDefenseAlgorithms()

    # Cargar algoritmos de ataque
    loadAttackTests()

    # Envio constante del estado del buffer al frontend
    bufferMonitorThread = threading.Thread(target=bufferMonitor, args=(socketio,), daemon=True)
    bufferMonitorThread.start()

    # Hilo de limpieza del buffer
    cleanerThread = threading.Thread(target=bufferCleaner, daemon=True)
    cleanerThread.start()

    return app
