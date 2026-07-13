from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


def load_prompt(path: str, *, base_dir: str | Path, role: str | None = None) -> str:
    """
    Load a plain-text or YAML chat prompt from a service-owned prompt directory.
    """
    return _load_prompt_cached(path, str(Path(base_dir).resolve()), role)


@lru_cache(maxsize=None)
def _load_prompt_cached(path: str, base_dir: str, role: str | None = None) -> str:
    prompt_path = Path(base_dir) / path

    if prompt_path.suffix in {".yaml", ".yml"}:
        return _load_yaml_prompt(prompt_path, role=role)

    return prompt_path.read_text(encoding="utf-8")


def _load_yaml_prompt(path: Path, role: str | None = None) -> str:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid prompt file {path}: expected mapping")

    prompt = data.get("prompt")

    if isinstance(prompt, str):
        if role is not None and role != "user":
            raise ValueError(f"Prompt role {role!r} not found in {path}")
        return prompt

    if not isinstance(prompt, list):
        raise ValueError(f"Invalid prompt format in {path}: expected string or messages list")

    contents: list[str] = []

    for item in prompt:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid prompt item in {path}: expected mapping")

        item_role = item.get("role")
        content = item.get("content")

        if role is not None and item_role != role:
            continue

        if not isinstance(content, str):
            raise ValueError(f"Invalid prompt content in {path}: expected string")

        contents.append(content)

    if role is not None and not contents:
        raise ValueError(f"Prompt role {role!r} not found in {path}")

    return "\n\n".join(contents)
