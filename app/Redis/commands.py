from typing import List


def ping(rest: List[str], *args, **kwargs) -> str:
    if not rest:
        return "PONG"
    else:
        return rest[0]
