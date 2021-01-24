import logging
import os
import socket
from functools import lru_cache
from inspect import getmembers, isfunction
from typing import Dict

from app.Redis import commands
from app.Redis.utils import is_windows, encode_ok_response, encode_error_response

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
                    conn.sendall(exec_command(data))


@lru_cache
def get_all_commands() -> Dict[str, object]:
    command_list: list = [x for x in getmembers(commands) if isfunction(x[1])]

    return {x[0]: x[1] for x in command_list}


def exec_command(data: bytes) -> bytes:
    try:
        data_str: str = data.decode()

        rest: list[str] = []
        command_string, *rest = data_str.split(' ')

        resp: str = get_all_commands()[command_string.lower()](rest)

        return encode_ok_response(resp)
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
