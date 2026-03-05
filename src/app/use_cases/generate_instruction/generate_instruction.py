from langchain_core.messages import SystemMessage, HumanMessage
from starlette.responses import JSONResponse

from app.policies.policies_loader import load_prompt
from app.use_cases.docx_to_html_graph.src.graph import compile_md_to_html_graph
from domain.services.converter import Converter
from domain.services.generate import AiGenerator
from infrastructure.llm.llm import LLMService

_ai_information_prompt = load_prompt('generation/ai_information.md').format(markdown_example=md_example,
                                                                            html_content_example=content_example)


class GenerateInstructionUseCase:
    def __init__(self, generator: AiGenerator):
        self._generator = generator
        self._llm = LLMService().openai()

    async def convert(self, md: str) -> JSONResponse:
        text = self._llm.ainvoke(
            [SystemMessage(content=DOC_TO_MENU_HTML_PROMPT.strip()),
             HumanMessage(content=state.html_content),
             ]
        )

        result = await compile_md_to_html_graph.ainvoke(
            {"mdFile": md}
        )

        return JSONResponse({"html_menu": result.get('html_menu'), "html_content": result.get('html_content')})
