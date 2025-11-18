from converter_data.domain.services.converter import Converter


class ConverterUseCase:
    def __init__(self, converter: Converter):
        self._converter = converter

    def convert(self, file_bytes: bytes):
        return self._converter.convert(file_bytes)