from io import BytesIO
from .base import RakNetDataType


# i16
class Short(RakNetDataType):
    byte_size = 2

    def __init__(self, value: int):
        if value < -(2**15) or value > 2**15 - 1:
            raise ValueError("Short value out of range")
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(2, "big", signed=True)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Short":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return Short(int.from_bytes(data, "big", signed=True))

    def __repr__(self):
        return f"Short({self.value})"
