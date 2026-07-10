from typing import Protocol


class AiGenerator(Protocol):
    async def generate(self, md: str):
        # Implement conversion logic here
        pass
