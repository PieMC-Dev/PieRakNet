from pieraknet.packets.packet import Packet

class OpenConnectionRequest2(Packet):
    PACKET_ID = 0x07
    PACKET_TYPE = 'open_connection_request_2'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.magic: bytes = None
        self.server_address: tuple = None
        self.mtu_size: int = None
        self.client_guid: int = None

    def decode_payload(self):
        self.magic = self.read_magic()
        self.server_address = self.read_address()
        self.mtu_size = self.read_short()
        self.client_guid = self.read_long()
