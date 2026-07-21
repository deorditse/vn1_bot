from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage

from app.policies.policies_loader import load_prompt
from common.enums import NonMedicineCategory
from domain.services.converter import Converter
from infrastructure.llm.llm import LLMService


class ShortDescriptionUseCase:
    ai_information_prompt = load_prompt('generation/ai_information.yaml')

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


class NonMedicineShortDescriptionUseCase:
    common_prompt_path = 'generation/ai_information_non_medicine_common.yaml'
    category_prompt_paths = {
        NonMedicineCategory.DIETARY_SUPPLEMENT: 'generation/ai_information_non_medicine_bad.yaml',
        NonMedicineCategory.MEDICAL_NUTRITION: 'generation/ai_information_non_medicine_medical_nutrition.yaml',
        NonMedicineCategory.MEDICAL_DEVICE: 'generation/ai_information_non_medicine_medical_device.yaml',
        NonMedicineCategory.HYGIENE: 'generation/ai_information_non_medicine_hygiene.yaml',
        NonMedicineCategory.COSMETICS: 'generation/ai_information_non_medicine_cosmetics.yaml',
    }

    def __init__(self, converter: Converter):
        self._converter = converter

    async def generate(self, file_bytes: bytes, category: NonMedicineCategory) -> str:
        md: str = await self._converter.convert(file_bytes=file_bytes)

        return await self.generate_from_markdown(md=md, category=category)

    async def generate_from_markdown(self, md: str, category: NonMedicineCategory) -> str:
        response = await LLMService().openai().ainvoke(
            [
                SystemMessage(content=self._build_category_system_prompt(category).strip()),
                HumanMessage(content=md),
            ]
        )

        return response.content.strip()

    @classmethod
    @lru_cache(maxsize=len(category_prompt_paths))
    def _build_category_system_prompt(cls, category: NonMedicineCategory) -> str:
        common_prompt_content = cls._get_common_prompt_content().strip()
        category_prompt_content = load_prompt(cls.category_prompt_paths[category]).strip()

        return "\n\n".join([common_prompt_content, category_prompt_content])

    @classmethod
    @lru_cache(maxsize=1)
    def _get_common_prompt_content(cls) -> str:
        return load_prompt(cls.common_prompt_path)
