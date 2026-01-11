from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).parent / "prompts"


@lru_cache(maxsize=None)
def load_prompt(path: str) -> str:
    """
    Загружает prompt один раз и кеширует его.
    """
    return (BASE_DIR / path).read_text(encoding="utf-8")
