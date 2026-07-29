from __future__ import annotations

import json
import os
from collections import OrderedDict

from app.config import settings
from domain.models.source import GitLabSource
from infrastructure.gitlab.prompts import get_prompt
from infrastructure.llm import LLMService
from vn1_markdown import normalize_generated_markdown, sanitize_markdown_inline


class GitLabAnswerService:
    """Формирует человекочитаемый ответ по найденным GitLab источникам."""

    async def build_answer(self, *, query: str, sources: list[GitLabSource]) -> str:
        fallback = self.build_fallback_answer(sources)
        if not settings.gitlab_answer_use_llm:
            return fallback
        if settings.gitlab_query_planner_provider != "openai":
            return fallback
        if not os.getenv(settings.gitlab_query_planner_token_env):
            return fallback

        payload = self._build_grouped_sources_payload(sources)

        try:
            prompt = get_prompt("answer").add_user_message(
                json.dumps(
                    {
                        "question": query,
                        "repositories": payload,
                    },
                    ensure_ascii=False,
                )
            )
            response = await LLMService().openai().ainvoke(
                prompt.format("tuple_list")
            )
            content = normalize_generated_markdown(response.content)
            return content or fallback
        except Exception:
            return fallback

    @staticmethod
    def build_fallback_answer(sources: list[GitLabSource]) -> str:
        lines = ["### Найденные места в GitLab"]
        visible_count = 0
        for repository_id, repository_sources in GitLabAnswerService._group_sources_by_repository(sources).items():
            lines.append(f"\n#### Репозиторий `{repository_id}`")
            for index, source in enumerate(repository_sources[: settings.gitlab_answer_max_sources], start=1):
                visible_count += 1
                lines.append(
                    f"{index}. **{sanitize_markdown_inline(source.title)}**\n"
                    f"   Описание: {sanitize_markdown_inline(source.description)}\n"
                    f"   URL: [открыть в GitLab]({source.url})"
                )
        if len(sources) > visible_count:
            lines.append(f"\nПоказаны {visible_count} из {len(sources)} найденных мест.")
        return normalize_generated_markdown("\n".join(lines))

    @staticmethod
    def _build_grouped_sources_payload(sources: list[GitLabSource]) -> list[dict[str, object]]:
        repositories: list[dict[str, object]] = []
        for repository_id, repository_sources in GitLabAnswerService._group_sources_by_repository(sources).items():
            visible_sources = repository_sources[: settings.gitlab_answer_max_sources]
            project_path = visible_sources[0].project_path if visible_sources else ""
            repositories.append(
                {
                    "repository_id": repository_id,
                    "project_path": project_path,
                    "total_sources": len(repository_sources),
                    "sources": [
                        {
                            "title": source.title,
                            "description": source.description,
                            "snippet": source.snippet,
                            "matched_query": source.matched_query,
                            "file_path": source.file_path,
                            "line": source.line,
                            "url": source.url,
                        }
                        for source in visible_sources
                    ],
                }
            )

        return repositories

    @staticmethod
    def _group_sources_by_repository(sources: list[GitLabSource]) -> OrderedDict[str, list[GitLabSource]]:
        grouped: OrderedDict[str, list[GitLabSource]] = OrderedDict()
        for source in sources:
            grouped.setdefault(source.repository_id, []).append(source)
        return grouped
