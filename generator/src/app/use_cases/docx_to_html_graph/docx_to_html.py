from app.use_cases.docx_to_html_graph.src.graph import compile_md_to_html_graph
from domain.services.converter import Converter


class ToHtmlConverterUseCase:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, file_bytes: bytes) -> dict:
        md: str = await self._converter.convert(file_bytes=file_bytes)

        return await self.convert_markdown(md)

    async def convert_markdown(self, md: str) -> dict:

        result = await compile_md_to_html_graph().ainvoke(
            {"mdFile": md}
        )

        return {
            "html_menu": str(result.get("html_menu", "")),
            "html_content": str(result.get("html_content", "")),
        }
