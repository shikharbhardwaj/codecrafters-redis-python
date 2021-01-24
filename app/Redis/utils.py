import os


def is_windows():
    return os.name == 'nt'


def encode_ok_response(resp: str) -> bytes:
    return f"+{resp}\r\n".encode()


def encode_error_response(resp: str) -> bytes:
    return f"-{resp}\r\n".encode()
