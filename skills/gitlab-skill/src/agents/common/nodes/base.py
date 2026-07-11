from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseNode(ABC):
    step: str
    title: str

    def __init__(self, step: str, title: str) -> None:
        self.step = step
        self.title = title

    @abstractmethod
    async def __call__(self, state: Any) -> Any:
        raise NotImplementedError
