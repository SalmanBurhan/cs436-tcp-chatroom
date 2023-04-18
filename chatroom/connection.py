from typing import NamedTuple
import asyncio

class Connection(NamedTuple):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    host:   str
    port:   int