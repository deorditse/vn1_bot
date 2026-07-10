from langchain_core.messages import HumanMessage, SystemMessage

from app.policies.policies_loader import load_prompt
from domain.services.converter import Converter
from infrastructure.llm.llm import LLMService


class ShortDescriptionUseCase:
    ai_information_prompt = load_prompt('generation/ai_information.md')

    def __init__(self, converter: Converter):
        self._converter = converter

    async def generate(self, file_bytes: bytes) -> str:
        md: str = await self._converter.convert(file_bytes=file_bytes)

        return await self.generate_from_markdown(md)

    async def generate_from_markdown(self, md: str) -> str:
        response = await LLMService().openai().ainvoke(
            [
                SystemMessage(content=self.ai_information_prompt.strip()),
                HumanMessage(content=md),
            ]
        )

        return response.content.strip()
