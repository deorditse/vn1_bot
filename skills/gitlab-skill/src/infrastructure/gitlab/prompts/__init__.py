from __future__ import annotations

from pathlib import Path

from vn1_prompts.system_prompt_loader import Prompt, get_prompt as _get_prompt, load_prompt as _load_prompt

PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    return _load_prompt(name, prompts_dir=PROMPTS_DIR)


def get_prompt(name: str) -> Prompt:
    return _get_prompt(name, prompts_dir=PROMPTS_DIR)
