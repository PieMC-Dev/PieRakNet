from io import BytesIO
from .base import RakNetDataType


# u16
class UnsignedShort(RakNetDataType):
    byte_size = 2

    def __init__(self, value: int):
        if value < 0 or value > 2**16 - 1:
            raise ValueError("UnsignedShort value out of range")
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(2, "big", signed=False)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "UnsignedShort":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return UnsignedShort(int.from_bytes(data, "big", signed=False))

    def __repr__(self):
        return f"UnsignedShort({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, UnsignedShort):
            return False
        return self.value == other.value
