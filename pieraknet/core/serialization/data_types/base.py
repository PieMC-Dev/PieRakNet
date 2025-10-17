from abc import ABC, ABCMeta, abstractmethod
from typing import Self, Type, overload, cast
from io import BytesIO


class RakNetDataUnion:
    def __init__(self, data_types: list["RakNetDataType"]):
        self.data_types = data_types

    def serialize(self) -> bytes:
        return b"".join([data_type.serialize() for data_type in self.data_types])

    @classmethod
    def deserialize(
        cls, data: bytes | BytesIO, data_types: list[Type["RakNetDataType"]]
    ) -> "RakNetDataUnion":
        if not isinstance(data, BytesIO):
            data = BytesIO(data)
        return RakNetDataUnion(
            [data_type.deserialize(data) for data_type in data_types]
        )

    def __repr__(self) -> str:
        return f"RakNetUnion({[', '.join([repr(data_type) for data_type in self.data_types])]})"

    @property
    def byte_size(self) -> int | None:
        byte_sizes = [data_type.byte_size for data_type in self.data_types]
        if None in byte_sizes:
            return None
        byte_sizes_filtered: list[int] = [bs for bs in byte_sizes if bs is not None]
        return sum(byte_sizes_filtered)

    @overload
    def __add__(self, other: bytes) -> bytes: ...

    @overload
    def __add__(self, other: "RakNetDataType") -> "RakNetDataUnion": ...

    @overload
    def __add__(self, other: "RakNetDataUnion") -> "RakNetDataUnion": ...

    def __add__(
        self, other: "RakNetDataType | RakNetDataUnion | bytes | BytesIO"
    ) -> "RakNetDataUnion | bytes | BytesIO":
        if isinstance(other, RakNetDataUnion):
            return RakNetDataUnion(self.data_types + other.data_types)
        if isinstance(other, RakNetDataType):
            return RakNetDataUnion(self.data_types + [other])
        if isinstance(other, bytes):
            return (
                b"".join([data_type.serialize() for data_type in self.data_types])
                + other
            )
        if isinstance(other, BytesIO):
            other.write(
                b"".join([data_type.serialize() for data_type in self.data_types])
            )
            return other

        raise NotImplementedError

    def __radd__(self, other: bytes | BytesIO) -> bytes | BytesIO:
        if isinstance(other, bytes):
            return other + b"".join(
                [data_type.serialize() for data_type in self.data_types]
            )

        raise NotImplementedError

    def __iter__(self):
        return iter(self.data_types)

    def __len__(self) -> int:
        return len(self.data_types)

    def __getitem__(self, index: int) -> "RakNetDataType":
        return self.data_types[index]


class RakNetTypeUnion:
    def __init__(self, data_types: list[Type["RakNetDataType"]]):
        self.data_types = data_types

    def __repr__(self) -> str:
        type_names = ", ".join([dt.__name__ for dt in self.data_types])
        return f"RakNetTypeUnion({type_names})"

    def __call__(self, *values) -> RakNetDataUnion:
        if len(values) != len(self.data_types):
            raise ValueError(
                f"Expected {len(self.data_types)} values, got {len(values)}"
            )
        instances = [dt(val) for dt, val in zip(self.data_types, values)]
        return RakNetDataUnion(instances)

    def deserialize(self, data: bytes | BytesIO) -> RakNetDataUnion:
        return RakNetDataUnion.deserialize(data, self.data_types)

    @property
    def byte_size(self) -> int | None:
        byte_sizes: list[int | None] = [dt.byte_size for dt in self.data_types]
        if None in byte_sizes:
            return None
        byte_sizes_filtered: list[int] = [bs for bs in byte_sizes if bs is not None]
        return sum(byte_sizes_filtered)


class RakNetTypeMeta(ABCMeta):
    def __add__(cls, other: Type["RakNetDataType"]) -> RakNetTypeUnion:
        cls_typed = cast(Type["RakNetDataType"], cls)
        if isinstance(other, RakNetTypeMeta):
            other_typed = cast(Type["RakNetDataType"], other)
            return RakNetTypeUnion([cls_typed, other_typed])
        if isinstance(other, RakNetTypeUnion):
            return RakNetTypeUnion([cls_typed] + other.data_types)
        raise TypeError(
            f"unsupported operand type(s) for +: '{cls.__name__}' and '{type(other).__name__}'"
        )

    def __radd__(cls, other: RakNetTypeUnion) -> RakNetTypeUnion:
        cls_typed = cast(Type["RakNetDataType"], cls)
        if isinstance(other, RakNetTypeUnion):
            return RakNetTypeUnion(other.data_types + [cls_typed])
        raise TypeError(
            f"unsupported operand type(s) for +: '{type(other).__name__}' and '{cls.__name__}'"
        )


class RakNetDataType(ABC, metaclass=RakNetTypeMeta):
    byte_size: int | None = None

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "byte_size"):
            raise NotImplementedError("byte_size must be defined")

    @abstractmethod
    def serialize(self) -> bytes: ...

    @abstractmethod
    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> Self: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @overload
    def __add__(self, other: bytes) -> bytes: ...

    @overload
    def __add__(self, other: "RakNetDataType") -> "RakNetDataUnion": ...

    @overload
    def __add__(self, other: "RakNetDataUnion") -> "RakNetDataUnion": ...

    def __add__(
        self, other: "RakNetDataType | RakNetDataUnion | bytes"
    ) -> "RakNetDataUnion | bytes":
        if isinstance(other, RakNetDataUnion):
            return RakNetDataUnion([self]) + other
        if isinstance(other, RakNetDataType):
            return RakNetDataUnion([self, other])
        if isinstance(other, bytes):
            return self.serialize() + other

        raise NotImplementedError

    def __radd__(self, other: bytes) -> bytes:
        if isinstance(other, bytes):
            return other + self.serialize()

        raise NotImplementedError
