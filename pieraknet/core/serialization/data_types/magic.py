from io import BytesIO
from .base import RakNetDataType

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")


class Magic(RakNetDataType):
    byte_size = 16

    def serialize(self) -> bytes:
        return MAGIC

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "Magic":
        data = data.read(cls.byte_size) if isinstance(data, BytesIO) else data
        if data != MAGIC:
            raise ValueError("Magic value does not match")
        return Magic()

    def __repr__(self):
        return "Magic()"
