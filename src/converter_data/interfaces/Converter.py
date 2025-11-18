from typing import Protocol


class Converter(Protocol):
    def convert(self, bytes: bytes) :
        """Converter bytes to concert data"""
        ...
