from collections.abc import AsyncIterator
from typing import Any

from fastapi import Request
from app.config.skills import load_skill_descriptors
from common.enums import SkillEnum
from domain.auth import User
from domain.models.skill import SkillDescriptor
from infrastructure.clients.http_stream import HttpStreamClient


class SkillClient(HttpStreamClient):
    def __init__(self, descriptor: SkillDescriptor) -> None:
        super().__init__(descriptor.base_url)
        self.descriptor = descriptor

    async def manifest(self) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}{self.descriptor.manifest_path}")
            response.raise_for_status()
            return response.json()

    async def stream_json_bytes_as_user(
        self,
        request: Request,
        payload: dict[str, Any],
        current_user: User,
    ) -> AsyncIterator[bytes]:
        async for chunk in self.stream_json_bytes(
            request=request,
            path=self.descriptor.stream_path,
            payload=payload,
            extra_headers=self._user_headers(current_user),
        ):
            yield chunk

    @staticmethod
    def _user_headers(current_user: User) -> dict[str, str]:
        headers = {}
        if current_user.access_token:
            headers["Authorization"] = f"Bearer {current_user.access_token}"
        return headers


class SkillClientRegistry:
    def __init__(self, skills: list[SkillDescriptor]) -> None:
        self._descriptors = {skill.id: skill for skill in skills if skill.enabled}
        self._clients = {skill.id: SkillClient(skill) for skill in skills if skill.enabled}

    @classmethod
    def from_settings(cls) -> "SkillClientRegistry":
        return cls(skills=load_skill_descriptors())

    def get(self, skill_id: SkillEnum | str) -> SkillClient | None:
        skill_id = SkillEnum(skill_id)
        return self._clients.get(skill_id)

    def skill_ids(self) -> list[SkillEnum]:
        return sorted(self._clients)

    def accessible_skill_ids(self, user_roles: list[str]) -> list[SkillEnum]:
        return sorted(
            skill_id
            for skill_id, descriptor in self._descriptors.items()
            if self._has_required_roles(descriptor=descriptor, user_roles=user_roles)
        )

    def available_skills(self, user_roles: list[str] | None = None) -> list[dict]:
        roles = user_roles or []
        return [
            {
                "id": descriptor.id.value,
                "name": descriptor.name,
                "description": descriptor.description,
                "required_roles": descriptor.required_roles,
            }
            for descriptor in self._descriptors.values()
            if self._has_required_roles(descriptor=descriptor, user_roles=roles)
        ]

    @staticmethod
    def _has_required_roles(descriptor: SkillDescriptor, user_roles: list[str]) -> bool:
        if not descriptor.required_roles:
            return True
        return set(descriptor.required_roles).issubset(set(user_roles))
