from io import BytesIO
from typing import cast
from .base import RakNetDataType, RakNetDataUnion
from .byte import Byte
from .unsigned_short import UnsignedShort
from .unsigned_integer import UnsignedInteger


class AddressV4(RakNetDataType):
    byte_size = 7
    ip_version = 4

    def __init__(self, host: tuple[int, int, int, int] | str, port: int):
        if isinstance(host, str):
            host_parts = tuple(int(part) for part in host.split("."))
            if len(host_parts) != 4:
                raise ValueError("Invalid IP address")
            host = cast(tuple[int, int, int, int], host_parts)
        self.host = host
        self.port = port

    def serialize(self) -> bytes:
        addr = Byte(self.ip_version)
        for byte in self.host:
            addr += Byte(byte)
        addr += UnsignedShort(self.port)
        return addr.serialize()

    @classmethod
    def deserialize(cls, buffer: bytes | BytesIO) -> "AddressV4":
        data = BytesIO(buffer) if not isinstance(buffer, BytesIO) else buffer
        ip_version = Byte.deserialize(data).value
        if ip_version != 4:
            raise ValueError("Invalid IP version")
        host = cast(
            tuple[int, int, int, int], tuple([Byte.deserialize(data) for _ in range(4)])
        )
        port = UnsignedShort.deserialize(data).value
        return AddressV4(host, port)

    def __repr__(self):
        return f"AddressV4({self.host}, {self.port})"


class AddressV6(RakNetDataType):
    byte_size = 29
    ip_version = 6

    def __init__(
        self,
        family: int,
        port: int,
        flow_info: int,
        address: tuple[
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
        ],
        scope_id: int,
    ):
        self.family = family
        self.port = port
        self.flow_info = flow_info
        self.address = address
        self.scope_id = scope_id

    def serialize(self) -> bytes:
        return (
            UnsignedInteger(self.family)
            + UnsignedShort(self.port)
            + UnsignedInteger(self.flow_info)
            + RakNetDataUnion([Byte(part) for part in self.address])
            + UnsignedInteger(self.scope_id)
        ).serialize()

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "AddressV6":
        data = BytesIO(data) if not isinstance(data, BytesIO) else data
        family = UnsignedInteger.deserialize(data).value
        port = UnsignedShort.deserialize(data).value
        flow_info = UnsignedInteger.deserialize(data).value
        address = cast(
            tuple[
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
                int,
            ],
            tuple([Byte.deserialize(data) for _ in range(16)]),
        )
        scope_id = UnsignedInteger.deserialize(data).value
        return AddressV6(family, port, flow_info, address, scope_id)

    def __repr__(self):
        return f"AddressV6({self.family}, {self.port}, {self.flow_info}, {self.address}, {self.scope_id})"


class AddressUnion(RakNetDataType):
    byte_size = None
    
    def __init__(self, ip_version: int, address: AddressV4 | AddressV6):
        self.ip_version = ip_version
        self.ip_address = address

    def serialize(self) -> bytes:
        if self.ip_version == 4:
            return self.ip_address.serialize()
        if self.ip_version == 6:
            return self.ip_address.serialize()
        raise ValueError("Invalid IP version")

    @classmethod
    def deserialize(cls, data: bytes | BytesIO) -> "AddressUnion":
        data = BytesIO(data) if not isinstance(data, BytesIO) else data
        ip_version = Byte.deserialize(data).value
        if ip_version == 4:
            address = AddressV4.deserialize(data)
        elif ip_version == 6:
            address = AddressV6.deserialize(data)
        else:
            raise ValueError("Invalid IP version")
        return AddressUnion(ip_version, address)

    def __repr__(self):
        return f"AddressUnion({self.ip_version}, {self.ip_address})"