from shua.struct.field import Field
from typing import Callable

class BytesField(Field, bytes):
    def __new__(cls, value: bytes | None = None, length: int | Callable[[dict], int] | None = None):
        if value is None:
            value = b''
        obj = super().__new__(cls, value)
        obj._length = length
        return obj

    def get_length(self, context: dict | None = None) -> int:
        if self._length is None:
            return len(self)
        elif callable(self._length):
            return self._length(context or {})
        else:
            return self._length

    def build(self, context=None) -> bytes:
        length = self.get_length(context)
        return self[:length]
    
    @classmethod
    def parse(cls, data: bytes, context: dict | None = None, length: int | Callable[[dict], int] | None = None) -> 'BytesField':
        if length is None:
            length = len(data)
        if callable(length):
            length = length(context or {})
        return cls(data[:length], length=length)

    def __repr__(self):
        return f"BytesField({bytes(self)!r}, length={self._length})"

    @property
    def value(self):
        return bytes(self)

__all__ = ("BytesField",)