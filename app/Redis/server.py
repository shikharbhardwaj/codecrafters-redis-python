import os
import socket

from app.Redis.utils import is_windows

HOST = os.environ.get("REDIS_HOST", "localhost")
LISTEN_PORT = int(os.environ.get("REDIS_LISTEN_PORT", 6379))
REUSE_PORT = not is_windows()


def listen():
    with socket.create_server((HOST, LISTEN_PORT), reuse_port=REUSE_PORT) as s:
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)
