from io import BytesIO
from .base import RakNetDataType


# u32
class UnsignedInteger(RakNetDataType):
    byte_size = 4

    def __init__(self, value: int):
        if value < 0 or value > 2**32 - 1:
            raise ValueError("UnsignedInteger value out of range")
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(4, "little", signed=False)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "UnsignedInteger":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return UnsignedInteger(int.from_bytes(data, "little", signed=False))

    def __repr__(self):
        return f"UnsignedInteger({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, UnsignedInteger):
            return False
        return self.value == other.value
