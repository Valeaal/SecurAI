
import time
from flask_socketio import SocketIO
from .packetCapture import packetBuffer

def bufferMonitor(socketio):
    print(f"Emitiendo estado del buffer")
    while True:
        time.sleep(0.2)
        socketio.emit('buffer_status', {'size': packetBuffer.qsize()})
        #print(f"Emitiendo desde el socket: {packetBuffer.qsize()}")
