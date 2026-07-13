from pathlib import Path

from vn1_prompts.policies_loader import load_prompt as _load_prompt

BASE_DIR = Path(__file__).parent / "prompts"


def load_prompt(path: str, role: str | None = None) -> str:
    return _load_prompt(path, base_dir=BASE_DIR, role=role)
