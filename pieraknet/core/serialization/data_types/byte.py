from io import BytesIO
from .base import RakNetDataType


class Byte(RakNetDataType):
    byte_size = 1

    def __init__(self, value: int):
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(1, "big", signed=False)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Byte":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return Byte(int.from_bytes(data, "big", signed=False))

    def __repr__(self):
        return f"Byte({self.value})"
