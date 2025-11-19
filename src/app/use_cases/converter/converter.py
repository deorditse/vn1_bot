from fastapi import  UploadFile
from domain.services.converter import Converter


class ConverterUseCase:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, file: UploadFile):
        file_bytes = await file.read()
        return self._converter.convert(file_bytes=file_bytes)