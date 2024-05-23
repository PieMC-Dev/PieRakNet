from pieraknet.packets.packet import Packet

class OfflinePong(Packet):
    PACKET_ID = 0x1c
    PACKET_TYPE = 'offline_pong'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.client_timestamp: int = None
        self.server_guid: int = None
        self.magic: bytes = None
        self.server_responseData: str = None

    def encode_payload(self):
        self.write_long(self.client_timestamp)
        self.write_long(self.server_guid)

        if not isinstance(self.magic, bytes):
            self.magic = str(self.magic).encode()

        self.write_magic(self.magic)
        self.write_string(self.server_responseData)
