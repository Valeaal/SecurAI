from app import socketio
from app import create_app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000)