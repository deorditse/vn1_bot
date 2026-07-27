from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage

from app.policies.policies_loader import load_prompt_text
from common.enums import NonMedicineCategory
from domain.services.converter import Converter
from infrastructure.llm.llm import LLMService


class NonMedicineShortDescriptionUseCase:
    common_prompt_path = 'generation/ai_information_non_medicine/common.md'
    category_prompt_paths = {
        NonMedicineCategory.DIETARY_SUPPLEMENT: 'generation/ai_information_non_medicine/бад/category_prompt.md',
        NonMedicineCategory.MEDICAL_NUTRITION: 'generation/ai_information_non_medicine/Лечебное питание/category_prompt.md',
        NonMedicineCategory.MEDICAL_DEVICE: 'generation/ai_information_non_medicine/Медизделия/category_prompt.md',
        NonMedicineCategory.HYGIENE: 'generation/ai_information_non_medicine/Средства_гигиены/category_prompt.md',
        NonMedicineCategory.COSMETICS: 'generation/ai_information_non_medicine/косметика/category_prompt.md',
    }
    category_input_example_paths = {
        NonMedicineCategory.DIETARY_SUPPLEMENT: 'generation/ai_information_non_medicine/бад/input_example.md',
        NonMedicineCategory.MEDICAL_NUTRITION: 'generation/ai_information_non_medicine/Лечебное питание/input_example.md',
        NonMedicineCategory.MEDICAL_DEVICE: 'generation/ai_information_non_medicine/Медизделия/input_example.md',
        NonMedicineCategory.HYGIENE: 'generation/ai_information_non_medicine/Средства_гигиены/input_example.md',
        NonMedicineCategory.COSMETICS: 'generation/ai_information_non_medicine/косметика/input_example.md',
    }
    category_output_example_paths = {
        NonMedicineCategory.DIETARY_SUPPLEMENT: 'generation/ai_information_non_medicine/бад/output_example.md',
        NonMedicineCategory.MEDICAL_NUTRITION: 'generation/ai_information_non_medicine/Лечебное питание/output_example.md',
        NonMedicineCategory.MEDICAL_DEVICE: 'generation/ai_information_non_medicine/Медизделия/output_example.md',
        NonMedicineCategory.HYGIENE: 'generation/ai_information_non_medicine/Средства_гигиены/output_example.md',
        NonMedicineCategory.COSMETICS: 'generation/ai_information_non_medicine/косметика/output_example.md',
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
        category_prompt_content = load_prompt_text(cls.category_prompt_paths[category]).strip()
        input_example = load_prompt_text(cls.category_input_example_paths[category]).strip()
        output_example = load_prompt_text(cls.category_output_example_paths[category]).strip()

        return common_prompt_content.format(
            category_prompt=category_prompt_content,
            input_example=input_example,
            output_example=output_example,
        )

    @classmethod
    @lru_cache(maxsize=1)
    def _get_common_prompt_content(cls) -> str:
        return load_prompt_text(cls.common_prompt_path)
