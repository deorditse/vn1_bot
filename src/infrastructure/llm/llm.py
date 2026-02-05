from langchain_openai import ChatOpenAI


# from langchain_gigachat import GigaChat

class LLMService:
    def __init__(
            self,
            system_message: str | None = None,
    ):
        self._system_message = system_message

    # def giga_chat(self, model: str = 'GigaChat-2-Max') -> GigaChat:
    #     from common.env import api_key_gigachat

    #     return GigaChat(
    #         model=model,
    #         credentials=api_key_gigachat(),
    #         scope="GIGACHAT_API_CORP",
    #         verify_ssl_certs=False,
    #         streaming=True
    #     )

    def openai(self, model: str = "gpt-4.1") -> ChatOpenAI:
        from common.env import api_key_openai

        return ChatOpenAI(
            api_key=api_key_openai(),
            http_async_client=make_async_http_client(),  # ← ТОЛЬКО ТАК
            model=model,
            max_tokens=32000,
        )

    def deepseek(self) -> ChatOpenAI:
        from common.env import api_key_deepseek

        return ChatOpenAI(
            api_key=api_key_deepseek(),
            base_url="https://api.deepseek.com",
            http_async_client=make_async_http_client(),  # ← ТОЛЬКО ТАК
        )


import httpx
from common.env import proxy_url


def make_async_http_client() -> httpx.AsyncClient:
    proxy = proxy_url()

    if proxy:
        return httpx.AsyncClient(
            proxy=proxy,
            timeout=httpx.Timeout(300.0),
            verify=True,
        )

    return httpx.AsyncClient(
        timeout=httpx.Timeout(300.0),
        verify=True,
    )
