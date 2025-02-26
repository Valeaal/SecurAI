from flask_socketio import SocketIO
from datetime import datetime, timezone

class AttackNotifier:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio

    def notifyAttack(self, moduleName: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        # print(f"Emitiendo notificación de ataque desde {moduleName} a las {timestamp}")
        self.socketio.emit("notify_attack", {"module_source": moduleName, "timestamp": timestamp})
