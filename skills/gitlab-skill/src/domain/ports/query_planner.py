from __future__ import annotations

from typing import Protocol


class GitLabQueryPlannerPort(Protocol):
    async def build_queries(self, query: str) -> list[str]:
        raise NotImplementedError
