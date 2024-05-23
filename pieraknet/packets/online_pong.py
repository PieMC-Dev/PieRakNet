from pieraknet.packets.packet import Packet

class OnlinePong(Packet):
    PACKET_ID = 0x03
    PACKET_TYPE = 'online_pong'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.client_timestamp: int = None
        self.server_timestamp: int = None

    def decode_payload(self):
        self.client_timestamp = self.read_long()
        self.server_timestamp = self.read_long()

    def encode_payload(self):
        self.write_long(self.client_timestamp)
        self.write_long(self.server_timestamp)
