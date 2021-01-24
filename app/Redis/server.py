import logging
import os
import socket
import types
from functools import lru_cache
from inspect import getmembers, isfunction
import selectors
from typing import Dict, List

from app.Redis import commands
from app.Redis.utils import is_windows, encode_ok_response, encode_error_response, decode_request

HOST = os.environ.get("REDIS_HOST", "localhost")
LISTEN_PORT = int(os.environ.get("REDIS_LISTEN_PORT", 6379))
REUSE_PORT = not is_windows()

sel = selectors.DefaultSelector()


def listen():
    with socket.create_server((HOST, LISTEN_PORT), reuse_port=REUSE_PORT) as sock:
        sock.listen()
        logging.info('Listening on ', (HOST, LISTEN_PORT))

        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, data=None)

        # Main event loop
        while True:
            events = sel.select(timeout=None)

            # Register functions (accept and service connections)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)


def accept_wrapper(sock: socket):
    conn, addr = sock.accept()

    logging.info('Connected by', addr)

    conn.setblocking(False)

    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    sel.register(conn, events, data=data)


def service_connection(key, mask: int):
    conn = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        # TODO: Fix max request size limit here.
        recv_data = conn.recv(1024)

        if recv_data:
            logging.debug("Received data of size: ", len(recv_data))
            data.outb += exec_command(recv_data)
        else:
            logging.info("Closing connection to: ", data.addr)
            sel.unregister(conn)
            conn.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = conn.send(data.outb)
            logging.debug("Sent data of size: ", len(data.outb))
            data.outb = data.outb[sent:]



@lru_cache
def get_all_commands() -> Dict[str, object]:
    command_list: list = [x for x in getmembers(commands) if isfunction(x[1])]

    return {x[0]: x[1] for x in command_list}


def exec_command(request_data: bytes) -> bytes:
    try:
        data_str: str = request_data.decode()

        request_list: List[str] = decode_request(data_str)

        command_string, *rest = request_list

        command = get_all_commands()[command_string.lower()]

        return command(rest)
    except UnicodeDecodeError as e:
        logging.exception("Could not decode request data, exception:", exc_info=e)

        return encode_error_response("Could not decode request data")
    except IndexError as e:
        logging.exception(f"Could not get command string from request data: {data_str}", exc_info=e)

        return encode_error_response("Could not get command string")
    except KeyError as e:
        logging.exception(f"Unsupported command: {command_string}", exc_info=e)

        return encode_error_response(f"Unsupported command: {command_string}")
    except Exception as e:
        logging.exception("Exception occurred when handling request", exc_info=e)

        return encode_error_response("Exception occurred when handling request")
