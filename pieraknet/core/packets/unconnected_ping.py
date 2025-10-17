from io import BytesIO
from typing import cast
from .base import BasePacket
from ..serialization.data_types import Long, Magic, Byte, MAGIC


class UnconnectedPing(BasePacket):
    PACKET_IDS = [0x01, 0x02]

    def __init__(
        self,
        timestamp: int,
        client_guid: int,
        magic: bytes | None = None,
        packet_id: int = 0x01,
    ):
        if packet_id not in self.PACKET_IDS:
            raise ValueError("Invalid packet ID")
        self.packet_id = packet_id
        self.timestamp = timestamp
        self.client_guid = client_guid
        self.magic = magic or MAGIC

    def serialize(self) -> bytes:
        return (
            Byte(self.packet_id)
            + Long(self.timestamp)
            + Magic(self.magic)
            + Long(self.client_guid)
        ).serialize()

    @classmethod
    def deserialize(
        cls, data: bytes | BytesIO, read_packet_id: bool = True
    ) -> "UnconnectedPing":
        data = data if isinstance(data, BytesIO) else BytesIO(data)

        if read_packet_id:
            packet_id, timestamp, magic, client_guid = cast(
                tuple[Byte, Long, Magic, Long],
                (Byte + Long + Magic + Long).deserialize(data),
            )
            if packet_id not in cls.PACKET_IDS:
                raise ValueError("Invalid packet ID")
        else:
            timestamp, magic, client_guid = cast(
                tuple[Long, Magic, Long], (Long + Magic + Long).deserialize(data)
            )

        return UnconnectedPing(
            timestamp.value, client_guid.value, magic.data, packet_id.value
        )

    def __repr__(self):
        return f"UnconnectedPing({self.timestamp}, {self.client_guid}, {self.magic}, {self.packet_id})"
