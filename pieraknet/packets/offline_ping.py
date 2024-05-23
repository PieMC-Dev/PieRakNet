from pieraknet.packets.packet import Packet

class OfflinePing(Packet):
    PACKET_ID = 0x01
    PACKET_TYPE = 'offline_ping'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.client_timestamp: int = None
        self.magic: bytes = None
        self.client_guid: int = None

    def decode_payload(self):
        self.client_timestamp = self.read_long()
        self.magic = self.read_magic()
        self.client_guid = self.read_long()
