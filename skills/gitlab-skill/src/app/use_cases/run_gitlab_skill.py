from collections.abc import AsyncIterator

from fastapi import Request

from app.api.schemas.skill import SkillRunRequest
from common.sse import fragment, sse_event, terminal_payload
from domain.services.gitlab_search import GitLabSearchService


class RunGitLabSkillUseCase:
    def __init__(self) -> None:
        self.search_service = GitLabSearchService()

    async def stream(self, request: Request, payload: SkillRunRequest) -> AsyncIterator[str]:
        request_id = payload.request_id or ""
        question = payload.message

        yield sse_event(
            {
                "data": fragment(
                    fragment_type="request",
                    status="success",
                    content=question,
                    request_id=request_id,
                    skill="gitlab",
                )
            }
        )
        yield sse_event(
            {
                "data": fragment(
                    fragment_type="search",
                    status="success",
                    content=f"Ищем в GitLab: {question}",
                    query=question,
                )
            }
        )

        results = await self.search_service.search(question)
        if await request.is_disconnected():
            return

        if not results:
            yield sse_event(
                terminal_payload(
                    "error",
                    [
                        fragment(
                            fragment_type="response",
                            status="error",
                            content="Не найдены подтвержденные источники в GitLab.",
                        )
                    ],
                )
            )
            return

        for result in results:
            yield sse_event(
                {
                    "data": fragment(
                        fragment_type="source",
                        status="success",
                        content=result.snippet,
                        source=result.model_dump(),
                    )
                }
            )

        yield sse_event(
            terminal_payload(
                "success",
                [
                    fragment(
                        fragment_type="response",
                        status="success",
                        content="GitLab skill пока работает в режиме заглушки. Подключите GitLab API в infrastructure/gitlab.",
                        sources=[result.model_dump() for result in results],
                    )
                ],
            )
        )
