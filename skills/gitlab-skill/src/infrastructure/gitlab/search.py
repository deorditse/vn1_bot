from __future__ import annotations

import os
from typing import Any

from app.config import GitLabRepositorySettings, settings
from domain.models.source import GitLabSource
from domain.ports import GitLabQueryPlannerPort, GitLabSearchPort
from infrastructure.gitlab.client import GitLabClient
from infrastructure.gitlab.query_planner import GitLabQueryPlanner


class GitLabSearchService(GitLabSearchPort):
    """Ищет код в заранее разрешенных GitLab-проектах."""

    def __init__(
        self,
        *,
        repositories: list[GitLabRepositorySettings] | None = None,
        query_planner: GitLabQueryPlannerPort | None = None,
    ) -> None:
        self.repositories = repositories if repositories is not None else settings.enabled_gitlab_repositories
        self.query_planner = query_planner or GitLabQueryPlanner()

    async def search(self, query: str, *, repository_ids: list[str] | None = None) -> list[GitLabSource]:
        if not query.strip():
            return []

        sources: list[GitLabSource] = []
        seen: set[tuple[str, str, str, int | None]] = set()
        queries = await self.query_planner.build_queries(query)
        for repository in self._select_repositories(repository_ids):
            client = self._build_client(repository)
            for search_query in queries:
                rows = await client.search_project_code(
                    project=repository.project_path,
                    query=search_query,
                    per_page=repository.per_project_limit or settings.gitlab_search_per_project_limit,
                )
                for source in self._map_rows(repository, client, rows, matched_query=search_query):
                    key = (source.repository_id, source.file_path, source.ref, source.line)
                    if key in seen:
                        continue
                    seen.add(key)
                    sources.append(source)
        return sources

    def _select_repositories(self, repository_ids: list[str] | None) -> list[GitLabRepositorySettings]:
        if not repository_ids:
            return self.repositories

        allowed_ids = set(repository_ids)
        selected = [repository for repository in self.repositories if repository.id in allowed_ids]
        return selected or self.repositories

    @staticmethod
    def _build_client(repository: GitLabRepositorySettings) -> GitLabClient:
        return GitLabClient(
            base_url=str(repository.base_url),
            token=os.getenv(repository.token_env, ""),
        )

    def _map_rows(
        self,
        repository: GitLabRepositorySettings,
        client: GitLabClient,
        rows: list[dict[str, Any]],
        *,
        matched_query: str,
    ) -> list[GitLabSource]:
        sources: list[GitLabSource] = []
        for index, row in enumerate(rows, start=1):
            path = str(row.get("path") or row.get("filename") or row.get("basename") or "unknown")
            ref = str(row.get("ref") or "main")
            start_line = self._to_int(row.get("startline"))
            code = str(row.get("data") or "").strip()
            title = f"{repository.id}:{path}"
            if start_line:
                title = f"{title}:{start_line}"

            sources.append(
                GitLabSource(
                    id=f"{repository.id}:{path}:{start_line or 0}:{index}",
                    title=title,
                    url=client.build_blob_url(project=repository.project_path, path=path, ref=ref, line=start_line),
                    source_type="code",
                    snippet=self._build_snippet(
                        repository_id=repository.id,
                        project=repository.project_path,
                        path=path,
                        line=start_line,
                        code=code,
                    ),
                    description=self._build_description(code, path),
                    matched_query=matched_query,
                    repository_id=repository.id,
                    project_path=repository.project_path,
                    file_path=path,
                    ref=ref,
                    line=start_line,
                )
            )
        return sources

    @staticmethod
    def _to_int(value: object) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _build_snippet(*, repository_id: str, project: str, path: str, line: int | None, code: str) -> str:
        location = f"[{repository_id}] {project}/{path}"
        if line:
            location = f"{location}:{line}"
        return f"{location}\n{code}" if code else location

    @staticmethod
    def _build_description(code: str, path: str) -> str:
        for line in code.splitlines():
            cleaned = " ".join(line.strip().split())
            if cleaned:
                return cleaned[: settings.gitlab_answer_max_description_chars]
        return f"Совпадение в файле {path}"
