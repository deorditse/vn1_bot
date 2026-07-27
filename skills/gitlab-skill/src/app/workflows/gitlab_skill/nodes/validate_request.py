from __future__ import annotations

import json
import os

from app.config import settings
from app.workflows.common.nodes import BaseNode
from app.workflows.gitlab_skill.app import GitLabSkillStep
from app.workflows.gitlab_skill.state import GitLabGraphState
from infrastructure.gitlab.prompts import get_prompt
from infrastructure.llm import LLMService
from pydantic import BaseModel, Field
from vn1_protocol.skill_streaming import emit_ui_event
from vn1_protocol.sse_protocol import FragmentStatus, FragmentType, TerminalStatus


class RequestValidation(BaseModel):
    is_valid: bool = Field(description="Whether the request may be processed by gitlab-skill.")
    reason: str = Field(description="Short Russian reason for the decision.")


class ValidateRequestNode(BaseNode):
    def __init__(self) -> None:
        super().__init__(step=GitLabSkillStep.validate_request, title="Validate request")

    async def __call__(self, state: GitLabGraphState) -> GitLabGraphState:
        stream = state["stream"]
        message = stream.payload.message.strip()
        stream.data["message"] = message

        if not message:
            emit_ui_event(
                stream,
                self.step,
                1,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Пустой запрос для GitLab skill.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        validation = await self._validate_with_llm(message)
        if validation is not None and not validation.is_valid:
            emit_ui_event(
                stream,
                self.step,
                1,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content=validation.reason or "Запрос не прошёл проверку безопасности.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        emit_ui_event(
            stream,
            self.step,
            1,
            status=FragmentStatus.success,
            content="### Запрос прошёл проверку",
        )
        return state

    @staticmethod
    async def _validate_with_llm(message: str) -> RequestValidation | None:
        if settings.gitlab_query_planner_provider != "openai":
            return None
        if not os.getenv(settings.gitlab_query_planner_token_env):
            return None

        prompt = get_prompt("validate_request").add_user_message(
            json.dumps(
                {
                    "message": message,
                },
                ensure_ascii=False,
            )
        )
        validator = LLMService().openai(model=settings.gitlab_query_planner_model).with_structured_output(
            RequestValidation
        )
        return await validator.ainvoke(prompt.format("tuple_list"))
