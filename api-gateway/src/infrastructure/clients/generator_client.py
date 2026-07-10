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
            extra_headers={
                "X-User-Id": str(current_user.id),
                "X-User-Name": current_user.username,
                "X-User-Email": current_user.email or "",
                "X-User-Roles": ",".join(current_user.roles),
            },
        )

    async def stream_json_as_user(self, request, path: str, payload: dict, current_user: User):
        return await self.stream_json(
            request=request,
            path=path,
            payload=payload,
            extra_headers={
                "X-User-Id": str(current_user.id),
                "X-User-Name": current_user.username,
                "X-User-Email": current_user.email or "",
                "X-User-Roles": ",".join(current_user.roles),
            },
        )
