"""Shared prompt loading helpers for VN1 services."""

from vn1_prompts.policies_loader import load_prompt
from vn1_prompts.system_prompt_loader import Prompt, get_prompt, load_system_prompt

__all__ = ["Prompt", "get_prompt", "load_prompt", "load_system_prompt"]
