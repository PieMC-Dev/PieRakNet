from io import BytesIO
from .base import RakNetDataType


# i64
class Long(RakNetDataType):
    byte_size = 8

    def __init__(self, value: int):
        if value < -(2**63) or value > 2**63 - 1:
            raise ValueError("Long value out of range")
        self.value = value

    def serialize(self) -> bytes:
        return self.value.to_bytes(8, "big", signed=True)

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Long":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        return Long(int.from_bytes(data, "big", signed=True))

    def __repr__(self):
        return f"Long({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Long):
            return False
        return self.value == other.value
