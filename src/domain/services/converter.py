from typing import Protocol

from fastapi import  UploadFile
class Converter(Protocol):
    def convert(self, file: UploadFile):
        # Implement conversion logic here
        pass