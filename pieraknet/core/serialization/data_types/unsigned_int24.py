from io import BytesIO
from .base import RakNetDataType


# u24
class UnsignedInt24(RakNetDataType):
    byte_size = 3

    def __init__(self, value: int):
        if value < 0 or value > 2**24 - 1:
            raise ValueError("UnsignedInt24 value out of range")
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(3, "little", signed=False)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "UnsignedInt24":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return UnsignedInt24(int.from_bytes(data, "little", signed=False))

    def __repr__(self):
        return f"UnsignedInt24({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, UnsignedInt24):
            return False
        return self.value == other.value
