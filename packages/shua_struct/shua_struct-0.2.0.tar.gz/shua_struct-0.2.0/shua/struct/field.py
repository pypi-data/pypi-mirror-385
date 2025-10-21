from typing import Any
from abc import ABC, abstractmethod

class Field(ABC):
    @abstractmethod
    def get_length(self, context: dict | None = None) -> int: ...

    @classmethod
    @abstractmethod
    def parse(cls, data: bytes, context: dict | None = None) -> Any: ...

    @abstractmethod
    def build(self, value: Any = None, context: dict | None = None) -> bytes: ...

__all__ = ("Field",)