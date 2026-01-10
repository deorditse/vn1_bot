from domain.services.converter import Converter


class ConverterUseCase:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, file_bytes: bytes):
        return self._converter.convert(file_bytes=file_bytes)
