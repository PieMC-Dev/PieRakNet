from io import BytesIO
from .base import RakNetDataType

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")


class Magic(RakNetDataType):
    byte_size = 16

    def serialize(self, data: bytes) -> bytes:
        return data

    @classmethod
    def deserialize(cls, data: bytes | BytesIO, check: bool = True) -> "Magic":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        if data != MAGIC and check:
            raise ValueError("Magic value does not match")
        return Magic()

    def __repr__(self):
        return "Magic()"
