from pieraknet.packets.packet import Packet


class OnlinePing(Packet):
    packet_id = 0x00
    packet_type = 'online_ping'

    client_timestamp: int = None

    def decode_payload(self):
        self.client_timestamp = self.read_long()

    def encode_payload(self):
        self.write_long(self.client_timestamp)
