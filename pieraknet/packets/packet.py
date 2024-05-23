from pieraknet.buffer import Buffer

class Packet(Buffer):
    PACKET_ID: int
    PACKET_TYPE: int

    def encode_header(self):
        self.write_packet_id(self.PACKET_ID)

    def decode_header(self):
        return self.read_packet_id()

    def encode(self):
        self.encode_header()
        if hasattr(self, 'encode_payload'):
            self.encode_payload()

    def decode(self):
        self.decode_header()
        if hasattr(self, 'decode_payload'):
            self.decode_payload()
