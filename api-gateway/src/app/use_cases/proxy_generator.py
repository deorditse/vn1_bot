from fastapi import Request
from fastapi.responses import StreamingResponse

from domain.auth import User
from infrastructure.clients.generator_client import GeneratorClient


class ProxyGeneratorUseCase:
    def __init__(self, generator_client: GeneratorClient | None = None) -> None:
        self.generator_client = generator_client or GeneratorClient()

    async def execute(self, request: Request, path: str, current_user: User) -> StreamingResponse:
        return await self.generator_client.proxy_as_user(request=request, path=path, current_user=current_user)
