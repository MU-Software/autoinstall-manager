from contextlib import suppress
from socket import gaierror, gethostbyaddr


def islocalhost(host: str) -> bool:
    with suppress(gaierror):
        return gethostbyaddr(host)[2] in (["127.0.0.1"], ["::1"])
    return False
