from pieraknet.packets.packet import Packet

class OpenConnectionReply2(Packet):
    PACKET_ID = 0x08
    PACKET_TYPE = 'open_connection_reply_2'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.magic: bytes = None
        self.server_guid: int = None
        self.client_address: tuple = None
        self.mtu_size: int = None
        self.encryption_enabled: bool = None

    def encode_payload(self):
        if not isinstance(self.magic, bytes):
            self.magic = str(self.magic).encode()
    
        self.write_magic(self.magic)
        self.write_long(self.server_guid)
        self.write_address(self.client_address)
        self.write_short(self.mtu_size)
        self.write_bool(self.encryption_enabled)
