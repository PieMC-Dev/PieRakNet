from pieraknet.packets.packet import Packet

class ConnectionRequestAccepted(Packet):
    PACKET_ID = 0x10  # 16
    PACKET_TYPE = 'connection_request_accepted'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.client_address: tuple = None
        self.system_index: int = None
        self.internal_ids: list[tuple] = None
        self.request_time: int = None
        self.accepted_time: int = None

    def encode_payload(self):
        self.write_address(self.client_address)
        self.write_short(self.system_index)
        for address in self.internal_ids:
            self.write_address(address)
        self.write_long(self.request_time)
        self.write_long(self.accepted_time)

    def decode_payload(self):
        self.client_address = self.read_address()
        self.system_index = self.read_short()
        self.internal_ids = [self.read_address() for _ in range(0, 10)]
        self.request_time = self.read_long()
        self.accepted_time = self.read_long()