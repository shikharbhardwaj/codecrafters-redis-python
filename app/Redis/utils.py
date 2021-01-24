import os
from typing import Tuple, Union, List


def is_windows():
    return os.name == 'nt'


# Examples
# "$6\r\nfoobar\r\n"
# "*1\r\n$4\r\nping\r\n"
# "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
#

REQUEST_DELIM: str = '\r\n'


def decode_request(request_str: str) -> Tuple[Union[list[str], str], int]:
    if request_str[0] == '*':
        # RESP array
        len_idx = request_str.find(REQUEST_DELIM)
        array_len = int(request_str[1:len_idx])

        consumed_len = len_idx + len(REQUEST_DELIM)

        req_array: List[str] = []

        for _ in range(array_len):
            remaining_str = request_str[consumed_len:]

            elem, delta = decode_request(remaining_str)

            req_array.append(elem)
            consumed_len += delta

        return req_array
    elif request_str[0] == '$':
        # RESP string
        len_idx = request_str.find(REQUEST_DELIM)
        str_len = int(request_str[1:len_idx])

        str_start_idx = len_idx + len(REQUEST_DELIM)
        str_end_idx = str_start_idx + str_len

        return request_str[str_start_idx:str_end_idx], str_end_idx + len(REQUEST_DELIM)


def encode_ok_response(resp: str) -> bytes:
    return f"+{resp}\r\n".encode()


def encode_error_response(resp: str) -> bytes:
    return f"-{resp}\r\n".encode()
