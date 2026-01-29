from starlette.responses import JSONResponse

from app.use_cases.docx_to_html_graph.src.graph import compile_md_to_html_graph
from domain.services.converter import Converter


class ToHtmlConverterUseCase:
    def __init__(self, converter: Converter):
        self._converter = converter

    async def convert(self, file_bytes: bytes) -> JSONResponse:
        md: str = await self._converter.convert(file_bytes=file_bytes)

        result = await compile_md_to_html_graph.ainvoke(
            {"mdFile": md}
        )

        return JSONResponse({"html_menu": result.get('html_menu'), "html_content": result.get('html_content')})
