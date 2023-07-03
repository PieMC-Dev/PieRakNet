from pieraknet.buffer import Buffer


class Packet(Buffer):
    packet_id: int = None
    packet_type: int = None

    def encode_header(self, data):
        self.write_packet_id(data)

    def decode_header(self):
        return self.read_packet_id()

    def encode(self):
        self.encode_header(self.packet_id)
        if hasattr(self, 'encode_payload'):
            self.encode_payload()

    def decode(self):
        self.decode_header()
        if hasattr(self, 'decode_payload'):
            self.decode_payload()
