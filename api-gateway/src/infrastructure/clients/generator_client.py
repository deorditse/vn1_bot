import json

from fastapi import Request
from fastapi.responses import Response

from app.config import settings
from domain.auth import User
from infrastructure.clients.http_stream import HttpStreamClient


class GeneratorClient(HttpStreamClient):
    def __init__(self) -> None:
        super().__init__(str(settings.generator_base_url))

    async def proxy_as_user(self, request: Request, path: str, current_user: User) -> Response:
        return await self.proxy(
            request=request,
            path=path,
            extra_headers=self._user_headers(current_user),
        )

    @staticmethod
    def _user_headers(current_user: User) -> dict[str, str]:
        headers = {
            "X-VN1-User-Id": str(current_user.id),
            "X-VN1-Username": current_user.username,
            "X-VN1-User-Role": current_user.role,
            "X-VN1-User-Roles": json.dumps(current_user.roles, ensure_ascii=False),
        }
        if current_user.email:
            headers["X-VN1-User-Email"] = current_user.email
        if current_user.access_token:
            headers["Authorization"] = f"Bearer {current_user.access_token}"
        return headers
