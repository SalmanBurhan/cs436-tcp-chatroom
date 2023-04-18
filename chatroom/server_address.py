from typing import NamedTuple

class ServerAddress(NamedTuple):
    host: str = '127.0.0.1'
    port: int = 1800
