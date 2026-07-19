from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


@dataclass
class Prompt:
    name: str | None = None
    project: str | None = None
    prompt: str | list[tuple[str, str]] = ""
    version: int | None = None
    labels: list[str] = field(default_factory=list)
    config: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.prompt, list):
            self.prompt = [(str(role), str(content)) for role, content in self.prompt]
            return
        if not isinstance(self.prompt, str):
            raise ValueError(f"Unsupported prompt type: {type(self.prompt)}")

    @property
    def is_chat(self) -> bool:
        return isinstance(self.prompt, list)

    def format(self, target_format: str) -> str | list[dict[str, str]] | list[tuple[str, str]] | list[Any]:
        if target_format == "string":
            return self._to_string()
        if target_format == "tuple_list":
            return self._to_tuple_list()
        if target_format == "dict_list":
            return [{"role": role, "content": content} for role, content in self._to_tuple_list()]
        if target_format == "langchain":
            return self._to_langchain()
        raise ValueError(f"Unknown prompt format: {target_format}")

    def compile(self, **variables: object) -> Prompt:
        prompt = deepcopy(self)

        def substitute(text: str) -> str:
            def repl(match: re.Match[str]) -> str:
                key = match.group(1)
                if key not in variables:
                    raise KeyError(f"Missing prompt variable: {key}")
                return str(variables[key])

            return _VAR_PATTERN.sub(repl, text)

        if isinstance(prompt.prompt, str):
            prompt.prompt = substitute(prompt.prompt)
        else:
            prompt.prompt = [(role, substitute(content)) for role, content in prompt.prompt]
        return prompt

    def add_message(self, role: str, content: str) -> Prompt:
        prompt = deepcopy(self)
        messages = prompt._to_tuple_list()
        messages.append((role, content))
        prompt.prompt = messages
        return prompt

    def add_user_message(self, content: str) -> Prompt:
        return self.add_message("user", content)

    def system_prompt(self) -> str:
        if isinstance(self.prompt, str):
            return self.prompt

        contents = [content for role, content in self.prompt if role == "system"]
        if not contents:
            raise ValueError(f"Prompt {self.name or '<unknown>'} has no system message")
        return "\n\n".join(contents)

    def _to_string(self) -> str:
        if isinstance(self.prompt, str):
            return self.prompt
        if len(self.prompt) == 1:
            return self.prompt[0][1]
        return self.system_prompt()

    def _to_tuple_list(self) -> list[tuple[str, str]]:
        if isinstance(self.prompt, list):
            return self.prompt.copy()
        return [("system", self.prompt)]

    def _to_langchain(self) -> list[Any]:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        messages: list[Any] = []
        for role, content in self._to_tuple_list():
            if role == "system":
                messages.append(SystemMessage(content=content))
            elif role in {"assistant", "ai"}:
                messages.append(AIMessage(content=content))
            else:
                messages.append(HumanMessage(content=content))
        return messages


def load_prompt(name: str, *, prompts_dir: str | Path) -> str:
    return get_prompt(name, prompts_dir=prompts_dir).system_prompt()


def get_prompt(name: str, *, prompts_dir: str | Path) -> Prompt:
    return deepcopy(_get_prompt_cached(name, str(Path(prompts_dir).resolve())))


@lru_cache(maxsize=None)
def _get_prompt_cached(name: str, prompts_dir: str) -> Prompt:
    path = Path(prompts_dir) / name
    if path.suffix not in {".yaml", ".yml"}:
        path = path.with_suffix(".yaml")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid prompt file: {path}")

    messages = _read_prompt_messages(data, path)
    if not messages:
        raise ValueError(f"Invalid prompt file: {path}")
    return Prompt(
        name=_optional_str(data.get("name")),
        project=_optional_str(data.get("project")),
        prompt=messages,
        version=data.get("version") if isinstance(data.get("version"), int) else None,
        labels=[str(label) for label in data.get("labels", []) if isinstance(label, str)],
        config=data.get("config") if isinstance(data.get("config"), dict) else None,
    )


def _read_prompt_messages(data: dict, path: Path) -> list[tuple[str, str]]:
    prompt = data.get("prompt")
    if not isinstance(prompt, list):
        return []

    messages: list[tuple[str, str]] = []
    for item in prompt:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid prompt item in {path}: expected mapping")

        role = item.get("role")
        if role not in {"system", "user", "assistant", "ai"}:
            raise ValueError(f"Invalid prompt role in {path}: {role}")

        content = item.get("content")
        if not isinstance(content, str):
            raise ValueError(f"Invalid prompt content in {path}: expected string")

        messages.append((str(role), content))

    return messages


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


load_system_prompt = load_prompt
