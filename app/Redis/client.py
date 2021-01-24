#!/usr/bin/env python3

import os
import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
LISTEN_PORT = int(os.environ.get("REDIS_LISTEN_PORT", 6379))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, LISTEN_PORT))
    s.sendall(b'*2\r\n$3\r\nGET\r\n$3\r\nhey\r\n$2\r\n42\r\n')
    data = s.recv(1024)

print('Received', repr(data))
