from io import BytesIO
from .base import RakNetDataType
from .unsigned_short import UnsignedShort

ALLOWED_CHARS = """!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ """


class String(RakNetDataType):
    byte_size = None

    def __init__(self, value: str):
        if not all(char in ALLOWED_CHARS for char in value):
            raise ValueError("String contains invalid characters")
        if len(value) > 2**16 - 1:
            raise ValueError("String is too long")
        self.value = value

    def serialize(self) -> bytes:
        if len(self.value) > 2**16 - 1:
            raise ValueError("String is too long")
        return UnsignedShort(len(self.value)) + self.value.encode("ascii")

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "String":
        if isinstance(data, BytesIO):
            length = UnsignedShort.deserialize(data.read(2)).value
        else:
            length = UnsignedShort.deserialize(data[:2]).value
        if length > 2**16 - 1:
            raise ValueError("String is too long")
        if isinstance(data, BytesIO):
            string = data.read(length).decode("ascii")
        else:
            string = str(data[2 : 2 + length], "ascii")
        return String(string)

    def __repr__(self):
        return f"String({self.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, String):
            return False
        return self.value == other.value
