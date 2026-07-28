from common.config import settings
from common.utils import get_env


def api_key_openai() -> str:
    return get_env("OPENAI_API_KEY", settings.openai_api_key)
