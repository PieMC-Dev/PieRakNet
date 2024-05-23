from pieraknet.packets.packet import Packet

class OpenConnectionReply1(Packet):
    PACKET_ID = 0x06
    PACKET_TYPE = 'open_connection_reply_1'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.magic: bytes = None
        self.server_guid: int = None
        self.use_security: bool = None
        self.mtu_size: int = None

    def encode_payload(self):
        if not isinstance(self.magic, bytes):
            self.magic = str(self.magic).encode()
    
        self.write_magic(self.magic)
        self.write_long(self.server_guid)
        self.write_bool(self.use_security)
        self.write_short(self.mtu_size)
