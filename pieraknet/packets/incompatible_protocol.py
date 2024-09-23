from pieraknet.packets.packet import Packet

class IncompatibleProtocol(Packet):
    PACKET_ID = 0x19
    PACKET_TYPE = 'incompatible_protocol'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.raknet_protocol_version: int = None
        self.magic: bytes = None
        self.server_guid: int = None

    def encode_payload(self):
        self.write_byte(self.raknet_protocol_version)
        self.write_magic(self.magic)
        self.write_long(self.server_guid)
