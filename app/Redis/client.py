#!/usr/bin/env python3

import os
import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
LISTEN_PORT = int(os.environ.get("REDIS_LISTEN_PORT", 6379))

set_cmd = b'*5\r\n$3\r\nSET\r\n$3\r\nhey\r\n$2\r\n42\r\n$2\r\nPX\r\n$4\r\n9999\r\n'
get_cmd = b'*2\r\n$3\r\nGET\r\n$3\r\nhey\r\n$2\r\n42\r\n'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, LISTEN_PORT))
    s.sendall(get_cmd)
    data = s.recv(1024)

print('Received', repr(data))
