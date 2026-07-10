from pathlib import Path
from typing import Any
import os
import tomllib

from common.enums import SkillEnum
from domain.models.skill import SkillDescriptor


CONFIG_PATH = Path(__file__).with_name("setting.toml")


def load_skill_descriptors() -> list[SkillDescriptor]:
    with CONFIG_PATH.open("rb") as file:
        raw_config = tomllib.load(file)

    raw_skills: dict[str, dict[str, Any]] = raw_config.get("skills", {})
    descriptors: list[SkillDescriptor] = []

    for raw_skill_id, config in raw_skills.items():
        skill_id = SkillEnum(raw_skill_id)
        base_url = os.getenv(f"{skill_id.value.upper()}_SKILL_BASE_URL") or config["base_url"]
        descriptors.append(
            SkillDescriptor(
                id=skill_id,
                name=config["name"],
                description=config.get("description", ""),
                base_url=base_url,
                stream_path=config.get("stream_path", "/v1/run/stream"),
                manifest_path=config.get("manifest_path", "/manifest"),
                enabled=bool(config.get("enabled", True)),
                required_roles=list(config.get("required_roles", [])),
            )
        )

    return descriptors
