from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse, Response


class HttpStreamClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def proxy(
        self,
        request: Request,
        path: str,
        extra_headers: dict[str, str] | None = None,
    ) -> Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        body = await request.body()
        headers = self._forward_headers(request)
        if extra_headers:
            headers.update(extra_headers)

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.request(
                    request.method,
                    url,
                    params=request.query_params,
                    content=body,
                    headers=headers,
                )
        except httpx.HTTPError as err:
            return self._proxy_error_response(request=request, err=err)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=self._response_headers(response),
            media_type=response.headers.get("content-type"),
        )

    async def stream_json_bytes(
        self,
        path: str,
        payload: dict[str, Any],
        request: Request,
        extra_headers: dict[str, str] | None = None,
    ) -> AsyncIterator[bytes]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._forward_headers(request)
        headers.update(
            {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        if extra_headers:
            headers.update(extra_headers)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=headers,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk

    @staticmethod
    def _forward_headers(request: Request) -> dict[str, str]:
        skip = {"host", "content-length", "connection"}
        return {key: value for key, value in request.headers.items() if key.lower() not in skip}

    @staticmethod
    def _response_headers(response: httpx.Response) -> dict[str, str]:
        skip = {"content-length", "content-encoding", "transfer-encoding", "connection"}
        return {key: value for key, value in response.headers.items() if key.lower() not in skip}

    @staticmethod
    def _proxy_error_response(request: Request, err: httpx.HTTPError) -> JSONResponse:
        status_code = 502
        details: dict[str, Any] = {"upstream_error": str(err)}
        if isinstance(err, httpx.HTTPStatusError):
            status_code = err.response.status_code
            details["upstream_status"] = err.response.status_code
            details["upstream_body"] = err.response.text[:1000]

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": "upstream_error",
                    "message": "Ошибка upstream-сервиса",
                    "details": details,
                },
                "request": {
                    "id": request.headers.get("x-request-id"),
                    "method": request.method,
                    "path": request.url.path,
                },
                "service": "api-gateway",
                "status": status_code,
            },
        )
