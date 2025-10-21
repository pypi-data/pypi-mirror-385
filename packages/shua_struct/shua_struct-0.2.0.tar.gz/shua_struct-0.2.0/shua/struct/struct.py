from typing import TypeVar, Any, dataclass_transform, ClassVar, Iterator
from shua.struct.field import Field
from abc import ABCMeta

@dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class StructMeta(ABCMeta):
    def __new__(cls, name, bases, namespace: dict):
        annotations: dict[str, Any] = namespace.get('__annotations__', {})
        fields_info: dict[str, tuple[type[Field], Field]] = namespace.setdefault("__fields_info__", {})

        for field_name, field_type in annotations.items():
            if field_name.startswith("_"):
                continue

            default = namespace.get(field_name, None)

            if not isinstance(field_type, type):
                raise TypeError(f"Field '{field_name}' annotation in class '{name}' must be a class, got {type(field_type)}")

            if not issubclass(field_type, Field):
                raise TypeError(f"Field '{field_name}' type in class '{name}' must be a subclass of Field")

            if default is not None and not isinstance(default, field_type):
                raise TypeError(f"Default value of field '{field_name}' in class '{name}' must be an instance of {field_type}, got {type(default)}")

            fields_info[field_name] = (field_type, default)

        return super().__new__(cls, name, bases, namespace)

T = TypeVar('T', bound='BinaryStruct')

class BinaryStruct(Field, metaclass=StructMeta):
    __fields_info__: ClassVar[dict[str, tuple[type[Field], Field]]]

    def __init__(self, **kwargs):
        for name, (field_type, default) in self.__fields_info__.items():
            value = kwargs.get(name, default() if callable(default) else default)
            if value is None:
                value = field_type()
            elif not isinstance(value, field_type):
                value = field_type(value)
            setattr(self, name, value)

    @classmethod
    def parse(cls: type[T], data: bytes, context: dict | None = None) -> T:
        ctx = dict(context or {})
        obj_kwargs = {}

        for name, (field_type, default) in cls.__fields_info__.items():
            field_length = (default if default is not None else field_type()).get_length(ctx) # 0 == False
            if field_length > len(data):
                raise ValueError(f"Insufficient data for field '{name}': expected {field_length}, got {len(data)}")

            field_data = data[:field_length]
            value = field_type.parse(field_data, ctx)
            data = data[field_length:]

            obj_kwargs[name] = value
            ctx[name] = value

        return cls(**obj_kwargs)

    def _iterate_fields(self, context: dict | None = None) -> Iterator[tuple[str, Field, dict[str, Any]]]:
        ctx = dict(context or {})
        for name, (_, _) in self.__fields_info__.items():
            value = getattr(self, name)
            ctx[name] = value
            yield name, value, ctx

    def get_length(self, context: dict | None = None) -> int:
        return sum(value.get_length(ctx) for _, value, ctx in self._iterate_fields(context))

    def build(self, context: dict | None = None) -> bytes:
        return b''.join(value.build(ctx) for _, value, ctx in self._iterate_fields(context))

    def __repr__(self):
        fields = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__fields_info__)
        return f"{self.__class__.__name__}({fields})"

    def __getitem__(self, key):
        return getattr(self, key)


__all__ = ('BinaryStruct',)