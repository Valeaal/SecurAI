from app import socketio
from app import createApp

app = createApp()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000, allow_unsafe_werkzeug=True)
