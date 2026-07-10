from app.config import settings
from domain.auth import User
from infrastructure.clients.http_stream import HttpStreamClient


class GeneratorClient(HttpStreamClient):
    def __init__(self) -> None:
        super().__init__(str(settings.generator_base_url))

    async def proxy_as_user(self, request, path: str, current_user: User):
        return await self.proxy(
            request=request,
            path=path,
            extra_headers=self._user_headers(current_user),
        )

    async def stream_json_as_user(self, request, path: str, payload: dict, current_user: User):
        return await self.stream_json(
            request=request,
            path=path,
            payload=payload,
            extra_headers=self._user_headers(current_user),
        )

    @staticmethod
    def _user_headers(current_user: User) -> dict[str, str]:
        headers = {}
        if current_user.access_token:
            headers["Authorization"] = f"Bearer {current_user.access_token}"
        return headers
