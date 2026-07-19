from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx


class GitLabClient:
    """Тонкий HTTP-клиент для GitLab API."""

    def __init__(self, *, base_url: str, token: str = "", timeout_s: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_s = timeout_s

    async def search_project_code(self, *, project: str, query: str, per_page: int) -> list[dict[str, Any]]:
        """Ищет совпадения по коду внутри одного GitLab-проекта."""

        project_id = quote(project, safe="")
        url = f"{self.base_url}/api/v4/projects/{project_id}/search"
        headers = {"PRIVATE-TOKEN": self.token} if self.token else {}
        params = {
            "scope": "blobs",
            "search": query,
            "per_page": min(max(per_page, 1), 100),
        }

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def build_blob_url(self, *, project: str, path: str, ref: str | None, line: int | None) -> str:
        """Собирает человекочитаемую ссылку на файл в GitLab UI."""

        encoded_path = quote(path, safe="/")
        target_ref = quote(ref or "main", safe="")
        line_suffix = f"#L{line}" if line else ""
        return f"{self.base_url}/{project}/-/blob/{target_ref}/{encoded_path}{line_suffix}"
