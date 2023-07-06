from pieraknet.packets.packet import Packet


class OpenConnectionRequest1(Packet):
    packet_id = 0x05
    packet_type = 'open_connection_request_1'

    magic: bytes = None
    protocol_version: int = None
    mtu_size: int = None

    def decode_payload(self):
        self.magic = self.read_magic()
        self.protocol_version = int(self.read_byte())
        self.mtu_size = len(self.read()) + 46
