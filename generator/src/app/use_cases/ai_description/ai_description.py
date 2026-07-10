from langchain_core.messages import HumanMessage, SystemMessage

from app.policies.policies_loader import load_prompt
from domain.services.converter import Converter
from infrastructure.llm.llm import LLMService


_llm = LLMService().openai()


class ShortDescriptionUseCase:
    ai_information_prompt = load_prompt('generation/ai_information.md')

    def __init__(self, converter: Converter):
        self._converter = converter

    async def generate(self, file_bytes: bytes) -> str:
        md: str = await self._converter.convert(file_bytes=file_bytes)

        return await self.generate_from_markdown(md)

    async def generate_from_markdown(self, md: str) -> str:
        response = await _llm.ainvoke(
            [
                SystemMessage(content=self.ai_information_prompt.strip()),
                HumanMessage(content=md),
            ]
        )

        return response.content.strip()
