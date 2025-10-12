from abc import ABC, abstractmethod
from typing import Self, Type, overload
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
        return sum(byte_sizes)  # pyright: ignore[reportArgumentType, reportCallIssue]

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


class RakNetDataType(ABC):
    byte_size: int | None = None

    def __init__(self):
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
