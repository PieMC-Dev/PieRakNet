from pieraknet.packets.packet import Packet


class OnlinePong(Packet):
    packet_id = 0x03
    packet_type = 'online_pong'

    client_timestamp: int = None
    server_timestamp: int = None

    def decode_payload(self):
        self.client_timestamp = self.read_long()
        self.server_timestamp = self.read_long()

    def encode_payload(self):
        self.write_long(self.client_timestamp)
        self.write_long(self.server_timestamp)
