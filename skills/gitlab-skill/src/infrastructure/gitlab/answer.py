from __future__ import annotations

import json
import os

from app.config import settings
from domain.models.source import GitLabSource
from infrastructure.gitlab.prompts import get_prompt
from infrastructure.llm import LLMService


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

        payload = [
            {
                "description": source.description,
                "repository_id": source.repository_id,
                "project_path": source.project_path,
                "file_path": source.file_path,
                "line": source.line,
                "url": source.url,
            }
            for source in sources[: settings.gitlab_answer_max_sources]
        ]

        try:
            prompt = get_prompt("answer").add_user_message(
                json.dumps(
                    {
                        "question": query,
                        "sources": payload,
                    },
                    ensure_ascii=False,
                )
            )
            response = await LLMService().openai().ainvoke(
                prompt.format("tuple_list")
            )
            content = str(response.content).strip()
            return content or fallback
        except Exception:
            return fallback

    @staticmethod
    def build_fallback_answer(sources: list[GitLabSource]) -> str:
        lines = ["### Найденные места в GitLab"]
        for index, source in enumerate(sources, start=1):
            line_suffix = f":{source.line}" if source.line else ""
            lines.append(
                f"{index}. **{source.description}**\n"
                f"   Репозиторий: `{source.repository_id}` (`{source.project_path}`)\n"
                f"   Место: `{source.file_path}{line_suffix}`\n"
                f"   Найдено по: `{source.matched_query}`\n"
                f"   Ссылка: [открыть в GitLab]({source.url})"
            )
        return "\n".join(lines)
