from pieraknet.packets.packet import Packet
import zlib


class GamePacket(Packet):
    packet_id = 0xfe
    packet_type = 'game_packet'

    body: bytes = None

    def decode_payload(self, decompress=True):
        self.body = self.read()
        if decompress:
            self.body = self.decompress(self.body)

    def encode_payload(self, compress=True):
        if compress:
            self.write(self.compress(self.body))
        else:
            self.write(self.body)

    @staticmethod
    def decompress(data):
        return zlib.decompress(data, -zlib.MAX_WBITS, 1024 * 1024 * 8)

    @staticmethod
    def compress(data):
        compress = zlib.compressobj(1, zlib.DEFLATED, -zlib.MAX_WBITS)
        compressed_data = compress.compress(data)
        compressed_data += compress.flush()
        return compressed_data
