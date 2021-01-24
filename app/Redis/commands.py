

def ping(rest: list[str], *args, **kwargs) -> str:
    if not rest:
        return "PONG"
    else:
        return rest[0]
