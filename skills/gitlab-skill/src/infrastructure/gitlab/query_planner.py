from __future__ import annotations

import json
import os
import re
from collections import OrderedDict

from app.config import settings
from domain.ports import GitLabQueryPlannerPort
from infrastructure.llm import LLMService
from infrastructure.gitlab.prompts import get_prompt


class GitLabQueryPlanner(GitLabQueryPlannerPort):
    """Строит поисковые термины для GitLab code search из произвольной фразы."""

    _cache: OrderedDict[str, list[str]] = OrderedDict()
    _cache_size = 256

    async def build_queries(self, query: str) -> list[str]:
        fallback_queries = self._build_fallback_queries(query)
        cache_key = self._cache_key(query)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if settings.gitlab_query_planner_provider != "openai" or not self._should_call_llm(query):
            self._save_cache(cache_key, fallback_queries)
            return fallback_queries

        planned_queries = await self._build_llm_queries(query)
        queries = self._merge_queries(fallback_queries, planned_queries)
        self._save_cache(cache_key, queries)
        return queries

    @staticmethod
    def _build_fallback_queries(query: str) -> list[str]:
        normalized = " ".join(query.strip().split())
        if not normalized:
            return []

        tokens = re.findall(r"[\w.-]{3,}", normalized, flags=re.UNICODE)
        camel_tokens = [
            token
            for token in tokens
            if any(char.isupper() for char in token[1:]) or "_" in token or "." in token or "-" in token
        ]
        return list(dict.fromkeys([normalized, *camel_tokens, *tokens]))

    @staticmethod
    def _should_call_llm(query: str) -> bool:
        normalized = " ".join(query.strip().split())
        words = re.findall(r"\w+", normalized, flags=re.UNICODE)
        if len(words) < settings.gitlab_query_planner_min_words:
            return False
        if normalized.isascii() and re.fullmatch(r"[\w./:-]+", normalized):
            return False
        return True

    async def _build_llm_queries(self, query: str) -> list[str]:
        token = os.getenv(settings.gitlab_query_planner_token_env, "")
        if not token:
            return []

        try:
            prompt = get_prompt("query_planner").add_user_message(query)
            response = await LLMService().openai().ainvoke(
                prompt.format("tuple_list")
            )
            content = str(response.content)
            parsed = self._parse_json_array(content)
        except Exception:
            return []

        if not isinstance(parsed, list):
            return []
        return [item for item in parsed if isinstance(item, str)]

    @staticmethod
    def _parse_json_array(content: str) -> object:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("[")
            end = cleaned.rfind("]")
            if start == -1 or end == -1 or end <= start:
                raise
            return json.loads(cleaned[start : end + 1])

    @staticmethod
    def _merge_queries(*query_groups: list[str]) -> list[str]:
        queries: list[str] = []
        for group in query_groups:
            for query in group:
                cleaned = " ".join(query.strip().split())
                if cleaned:
                    queries.append(cleaned)
        return list(dict.fromkeys(queries))[: settings.gitlab_query_planner_max_queries]

    @staticmethod
    def _cache_key(query: str) -> str:
        return " ".join(query.lower().strip().split())

    @classmethod
    def _save_cache(cls, key: str, queries: list[str]) -> None:
        cls._cache[key] = queries
        cls._cache.move_to_end(key)
        while len(cls._cache) > cls._cache_size:
            cls._cache.popitem(last=False)
