from typing import Protocol

class Converter(Protocol):
    async def convert(self, file_bytes: bytes):
        # Implement conversion logic here
        pass


