from __future__ import annotations

import os

import httpx
from langchain_openai import ChatOpenAI

from app.config import settings


class LLMService:
    """Фабрика LLM-клиентов для gitlab-skill."""

    def openai(self, model: str | None = None) -> ChatOpenAI:
        return ChatOpenAI(
            api_key=os.getenv(settings.gitlab_query_planner_token_env, ""),
            base_url=str(settings.gitlab_query_planner_base_url),
            http_async_client=make_async_http_client(),
            model=model or settings.gitlab_query_planner_model,
            temperature=0,
        )


def make_async_http_client() -> httpx.AsyncClient:
    proxy = proxy_url()
    if proxy:
        return httpx.AsyncClient(
            proxy=proxy,
            timeout=httpx.Timeout(120.0),
            verify=True,
        )

    return httpx.AsyncClient(
        timeout=httpx.Timeout(120.0),
        verify=True,
    )


def proxy_url() -> str | None:
    return (
        os.getenv("PROXY")
        or os.getenv("ALL_PROXY")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("all_proxy")
        or os.getenv("https_proxy")
        or os.getenv("http_proxy")
    )
