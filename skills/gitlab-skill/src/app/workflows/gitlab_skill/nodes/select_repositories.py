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


class RepositorySelection(BaseModel):
    repository_ids: list[str] = Field(description="GitLab repository ids to search in.")


class SelectRepositoriesNode(BaseNode):
    """Определяет через LLM, в каких GitLab-репозиториях искать."""

    _repository_descriptions = {
        "flutter_mobile_vn1": "Flutter mobile application repository for VN1 mobile app.",
        "backend_vn1": "VN1 backend API/server repository.",
    }

    def __init__(self) -> None:
        super().__init__(step=GitLabSkillStep.select_repositories, title="Select repositories")

    async def __call__(self, state: GitLabGraphState) -> GitLabGraphState:
        stream = state["stream"]
        if stream.data.get("terminal_status") == TerminalStatus.error or stream.data.get("client_disconnected"):
            return state

        if not settings.enabled_gitlab_repositories:
            emit_ui_event(
                stream,
                self.step,
                2,
                fragment_type=FragmentType.response,
                status=FragmentStatus.error,
                content="Нет enabled-репозиториев для GitLab поиска.",
            )
            stream.data["terminal_status"] = TerminalStatus.error
            return state

        question = stream.data["message"]
        repository_ids = await self._select_repository_ids_with_llm(question)
        state["selected_repository_ids"] = repository_ids

        emit_ui_event(
            stream,
            self.step,
            2,
            status=FragmentStatus.success,
            content=(
                "### Репозитории для поиска выбраны\n"
                f"Репозитории: {', '.join(f'`{repository_id}`' for repository_id in repository_ids)}"
            ),
        )
        return state

    async def _select_repository_ids_with_llm(self, query: str) -> list[str]:
        fallback = self._all_enabled_repository_ids()
        if settings.gitlab_query_planner_provider != "openai":
            return fallback
        if not os.getenv(settings.gitlab_query_planner_token_env):
            return fallback

        try:
            prompt = get_prompt("repository_selector").add_user_message(
                json.dumps(
                    {
                        "question": query,
                        "repositories": self._repository_payload(),
                    },
                    ensure_ascii=False,
                )
            )
            selector = LLMService().openai(model=settings.gitlab_repository_selector_model).with_structured_output(
                RepositorySelection
            )
            selection = await selector.ainvoke(prompt.format("tuple_list"))
        except Exception:
            return fallback

        selected = self._filter_enabled_repository_ids(selection.repository_ids)
        return selected or fallback

    @staticmethod
    def _all_enabled_repository_ids() -> list[str]:
        return [repository.id for repository in settings.enabled_gitlab_repositories]

    @classmethod
    def _repository_payload(cls) -> list[dict[str, str]]:
        return [
            {
                "id": repository.id,
                "project_path": repository.project_path,
                "description": cls._repository_descriptions.get(repository.id, ""),
            }
            for repository in settings.enabled_gitlab_repositories
        ]

    @classmethod
    def _filter_enabled_repository_ids(cls, repository_ids: list[object]) -> list[str]:
        enabled_ids = set(cls._all_enabled_repository_ids())
        selected = [repository_id for repository_id in repository_ids if isinstance(repository_id, str)]
        return [repository_id for repository_id in dict.fromkeys(selected) if repository_id in enabled_ids]
