# ruff: noqa: E701
from shua.struct.field import Field
import struct

class NumericField(Field):
    fmt: str
    _type: type = int
    _default = 0

    def __new__(cls, value=None):
        if value is None:
            value = cls._default
        return super().__new__(cls, cls._type(value))

    def build(self, context=None) -> bytes:
        return struct.pack(self.fmt, self._type(self))

    @classmethod
    def parse(cls, data: bytes, context=None):
        (value,) = struct.unpack_from(cls.fmt, data)
        return cls(cls._type(value))

    def get_length(self, context=None) -> int:
        return struct.calcsize(self.fmt)

# -------------------------------
class IntField(NumericField, int):
    _type = int
    _default = 0
# -------------------------------
class FloatField(NumericField, float):
    _type = float
    _default = 0.0
# -------------------------------
class Int8(IntField):   fmt = 'b'
class UInt8(IntField):  fmt = 'B'
class Int16(IntField):  fmt = '>h'
class UInt16(IntField): fmt = '>H'
class Int32(IntField):  fmt = '>i'
class UInt32(IntField): fmt = '>I'
class Int64(IntField):  fmt = '>q'
class UInt64(IntField): fmt = '>Q'
# -------------------------------
class Float16(FloatField): fmt = '>e'
class Float32(FloatField): fmt = '>f'
class Float64(FloatField): fmt = '>d'
# -------------------------------

__all__ = (
    "Int8","UInt8","Int16","UInt16","Int32","UInt32","Int64","UInt64",
    "Float16","Float32","Float64"
)
