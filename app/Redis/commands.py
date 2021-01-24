import time
from typing import List, Dict

from app.Redis.utils import encode_ok_response


def ping(rest: List[str], *args, **kwargs) -> bytes:
    if not rest:
        return encode_ok_response("PONG")
    else:
        return encode_ok_response(rest[0])


def echo(rest: List[str], *args, **kwargs) -> bytes:
    if not rest:
        raise ValueError("ECHO needs a parameter")
    else:
        return encode_ok_response(rest[0], bulk_str=True)


kv_map: Dict[str, str] = dict()
expiry_time: Dict[str, float] = dict()


def set(rest: List[str], *args, **kwargs) -> bytes:
    if len(rest) < 2:
        raise ValueError("SET needs 2 parameters")

    key, val = rest[0], rest[1]

    if len(rest) == 4 and rest[2].lower() == 'px':
        # We need to set expiry as well
        offset = int(rest[3])
        expiry_time[key] = time.time() + offset / 1000
    else:
        expiry_time[key] = -1

    kv_map[key] = val

    return encode_ok_response("OK")


def get(rest: List[str], *args, **kwargs) -> bytes:
    if not rest:
        raise ValueError("GET needs 1 parameters")

    key = rest[0]

    exp_time = expiry_time.get(key, -1)

    # Check if this key was expired.
    if exp_time != -1 and exp_time < time.time():
        del expiry_time[key]
        del kv_map[key]

    return encode_ok_response(kv_map.get(key, None), bulk_str=True)
