from __future__ import annotations

from typing import Protocol

from domain.models.source import GitLabSource


class GitLabSearchPort(Protocol):
    async def search(self, query: str, *, repository_ids: list[str] | None = None) -> list[GitLabSource]:
        raise NotImplementedError
