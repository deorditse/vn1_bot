from collections.abc import AsyncIterator
import asyncio

from fastapi import Request

from app.api.schemas.skill import SkillRunRequest
from app.config import settings
from app.workflows.gitlab_skill.app import GitLabSkillStep, gitlab_app
from vn1_protocol.sse import SkillProgressEmitter
from vn1_protocol.skill_streaming import SkillStreamState, emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, SkillId, TerminalStatus


class RunGitLabSkillUseCase:
    async def stream(self, request: Request, payload: SkillRunRequest) -> AsyncIterator[str]:
        state = SkillStreamState(
            request=request,
            payload=payload,
            progress=SkillProgressEmitter(skill=SkillId.gitlab, request_id=payload.request_id),
        )

        if settings.gitlab_skill_mock_enabled:
            async for event in self._mock_stream(state):
                yield event
            return

        async for _ in gitlab_app.astream({"stream": state}, stream_mode="updates"):
            for event in state.drain_events():
                yield event
            if state.data.get("client_disconnected"):
                return
            if state.data.get("terminal_status") == TerminalStatus.error:
                yield state.progress.terminal(TerminalStatus.error)
                return

        yield state.progress.terminal(TerminalStatus.success)

    async def _mock_stream(self, state: SkillStreamState) -> AsyncIterator[str]:
        query = state.payload.message or "запрос без текста"

        emit_ui_event(
            state,
            GitLabSkillStep.validate_request,
            1,
            status=FragmentStatus.in_progress,
            content="Проверяю запрос и готовлю mock-поиск по GitLab...",
        )
        for event in state.drain_events():
            yield event
        await asyncio.sleep(0.25)

        emit_ui_event(
            state,
            GitLabSkillStep.validate_request,
            1,
            status=FragmentStatus.success,
            content="Запрос принят. Mock-режим включён, реальные GitLab API не вызываются.",
        )
        for event in state.drain_events():
            yield event
        await asyncio.sleep(0.25)

        emit_ui_event(
            state,
            GitLabSkillStep.search_gitlab,
            2,
            status=FragmentStatus.success,
            content="Нашёл 2 демонстрационных результата: issue и merge request.",
            sources=[
                {
                    "title": "MOCK-101: Ошибка авторизации в локальном стенде",
                    "url": "https://gitlab.example.local/mock/issues/101",
                    "type": "issue",
                },
                {
                    "title": "MOCK-42: Добавить SSE proxy для skills",
                    "url": "https://gitlab.example.local/mock/merge_requests/42",
                    "type": "merge_request",
                },
            ],
        )
        for event in state.drain_events():
            yield event
        await asyncio.sleep(0.25)

        answer = (
            "Mock GitLab skill ответил в SSE-стриме.\n\n"
            f"Запрос: {query}\n\n"
            "Демонстрационный вывод: по запросу найдены условные материалы GitLab, "
            "которые показывают, что gateway корректно прокидывает промежуточные fragments "
            "и финальное сообщение. Для реального поиска отключите `GITLAB_SKILL_MOCK_ENABLED`."
        )
        emit_ui_event(
            state,
            GitLabSkillStep.build_response,
            3,
            fragment_type=FragmentType.response,
            status=FragmentStatus.success,
            content=answer,
            sources=[
                {
                    "title": "MOCK-101: Ошибка авторизации в локальном стенде",
                    "url": "https://gitlab.example.local/mock/issues/101",
                    "type": "issue",
                },
                {
                    "title": "MOCK-42: Добавить SSE proxy для skills",
                    "url": "https://gitlab.example.local/mock/merge_requests/42",
                    "type": "merge_request",
                },
            ],
        )
        for event in state.drain_events():
            yield event
        yield state.progress.terminal(TerminalStatus.success)
