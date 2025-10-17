from io import BytesIO
from .base import RakNetDataType


class Boolean(RakNetDataType):
    byte_size = 1

    def __init__(self, value: bool):
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(1, "big", signed=False)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Boolean":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return Boolean(bool(int.from_bytes(data, "big", signed=False)))

    def __repr__(self):
        return f"Boolean({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Boolean):
            return False
        return self.value == other.value
