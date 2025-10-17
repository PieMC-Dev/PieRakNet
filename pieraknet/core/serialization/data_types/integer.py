from io import BytesIO
from .base import RakNetDataType


# i32
class Integer(RakNetDataType):
    byte_size = 4

    def __init__(self, value: int):
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(4, "little", signed=True)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Integer":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return Integer(int.from_bytes(data, "little", signed=True))

    def __repr__(self):
        return f"Integer({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Integer):
            return False
        return self.value == other.value
