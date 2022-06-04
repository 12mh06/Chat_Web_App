import socketio
from website import create_app, socket_io
from flask_socketio import SocketIO

app = create_app()

if __name__ == '__main__':
    socket_io.run(app, debug=True)
