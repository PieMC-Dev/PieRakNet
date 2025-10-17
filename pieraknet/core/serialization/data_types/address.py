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

    @classmethod
    def from_str(cls, host: str, port: int) -> "AddressV4":
        host_parts = tuple(int(part) for part in host.split("."))
        if len(host_parts) != 4:
            raise ValueError("Invalid IP address")
        return cls(host_parts, port)

    def serialize(self) -> bytes:
        addr = Byte(self.ip_version)
        for byte in self.host:
            addr += Byte(byte)
        addr += UnsignedShort(self.port)
        return addr.serialize()

    @classmethod
    def deserialize(
        cls, buffer: bytes | BytesIO, read_ip_version: bool = True
    ) -> "AddressV4":
        data = BytesIO(buffer) if not isinstance(buffer, BytesIO) else buffer
        if read_ip_version:
            ip_version = Byte.deserialize(data).value
            if ip_version != 4:
                raise ValueError("Invalid IP version")
        host = cast(
            tuple[int, int, int, int],
            tuple([Byte.deserialize(data).value for _ in range(4)]),
        )
        port = UnsignedShort.deserialize(data).value
        return AddressV4(host, port)

    def __repr__(self):
        return f"AddressV4({self.host}, {self.port})"

    def __str__(self) -> str:
        return ".".join(str(part) for part in self.host) + ":" + str(self.port)

    def __eq__(self, other) -> bool:
        if not isinstance(other, AddressV4):
            return False
        return self.host == other.host and self.port == other.port


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

    @classmethod
    def from_str(
        cls,
        address: str,
        port: int,
        scope_id: int,
        family: int = 23,
        flow_info: int = 0,
    ) -> "AddressV6":
        # Handle IPv6 compressed notation (::)
        if "::" in address:
            # Split on :: to get left and right parts
            parts = address.split("::")
            if len(parts) > 2:
                raise ValueError("Invalid IPv6 address: multiple :: found")

            left_parts = parts[0].split(":") if parts[0] else []
            right_parts = parts[1].split(":") if len(parts) > 1 and parts[1] else []

            # Remove empty strings from splitting
            left_parts = [p for p in left_parts if p]
            right_parts = [p for p in right_parts if p]

            # Calculate how many zero groups to insert
            total_groups = len(left_parts) + len(right_parts)
            if total_groups > 8:
                raise ValueError("Invalid IPv6 address: too many groups")

            zero_groups = 8 - total_groups

            # Reconstruct the full address
            full_parts = left_parts + ["0"] * zero_groups + right_parts
        else:
            full_parts = address.split(":")

        if len(full_parts) != 8:
            raise ValueError("Invalid IPv6 address: must have 8 groups")

        # Convert hex strings to integers
        address_parts = tuple(int(part, 16) for part in full_parts)

        # Convert 8 16-bit values to 16 8-bit values (bytes)
        address_bytes = []
        for part in address_parts:
            # Each 16-bit value becomes 2 bytes (high byte, low byte)
            address_bytes.append((part >> 8) & 0xFF)  # High byte
            address_bytes.append(part & 0xFF)  # Low byte
        address_tuple = cast(
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
            tuple(address_bytes),
        )
        return cls(family, port, flow_info, address_tuple, scope_id)

    def serialize(self) -> bytes:
        return (
            Byte(self.ip_version)
            + UnsignedInteger(self.family)
            + UnsignedShort(self.port)
            + UnsignedInteger(self.flow_info)
            + RakNetDataUnion([Byte(part) for part in self.address])
            + UnsignedInteger(self.scope_id)
        ).serialize()

    @classmethod
    def deserialize(
        cls, data: bytes | BytesIO, read_ip_version: bool = True
    ) -> "AddressV6":
        data = BytesIO(data) if not isinstance(data, BytesIO) else data
        if read_ip_version:
            ip_version = Byte.deserialize(data).value
            if ip_version != 6:
                raise ValueError("Invalid IP version")
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
            tuple([Byte.deserialize(data).value for _ in range(16)]),
        )
        scope_id = UnsignedInteger.deserialize(data).value
        return AddressV6(family, port, flow_info, address, scope_id)

    def __repr__(self):
        return f"AddressV6({self.family}, {self.port}, {self.flow_info}, {self.address}, {self.scope_id})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, AddressV6):
            return False
        return (
            self.family == other.family
            and self.port == other.port
            and self.flow_info == other.flow_info
            and self.address == other.address
            and self.scope_id == other.scope_id
        )


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
            address = AddressV4.deserialize(data, False)
        elif ip_version == 6:
            address = AddressV6.deserialize(data, False)
        else:
            raise ValueError("Invalid IP version")
        return AddressUnion(ip_version, address)

    def __repr__(self):
        return f"AddressUnion({self.ip_version}, {self.ip_address})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, AddressUnion):
            return False
        return (
            self.ip_version == other.ip_version and self.ip_address == other.ip_address
        )
