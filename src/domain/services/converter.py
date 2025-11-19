from typing import Protocol
class Converter(Protocol):
    def convert(self, file_bytes: bytes):
        # Implement conversion logic here
        pass