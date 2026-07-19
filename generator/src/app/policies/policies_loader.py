from pathlib import Path

from vn1_prompts.system_prompt_loader import load_prompt as _load_prompt

BASE_DIR = Path(__file__).parent / "prompts"


def load_prompt(path: str) -> str:
    return _load_prompt(path, prompts_dir=BASE_DIR)
