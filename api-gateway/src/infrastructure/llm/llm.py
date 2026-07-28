import httpx
from langchain_openai import ChatOpenAI


class LLMService:
    def openai(self, model: str = "gpt-4.1") -> ChatOpenAI:
        from common.env import api_key_openai

        return ChatOpenAI(
            api_key=api_key_openai(),
            http_async_client=make_async_http_client(),
            model=model,
            temperature=0,
        )


def make_async_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(120.0),
        verify=True,
    )
