from pieraknet.packets.packet import Packet
import zlib

class GamePacket(Packet):
    PACKET_ID = 0xFE
    PACKET_TYPE = 'game_packet'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.body: bytes = None

    def decode_payload(self, decompress=True):
        self.body = self.read()
        if decompress:
            self.body = self._decompress(self.body)

    def encode_payload(self, compress=True):
        if compress:
            self.write(self._compress(self.body))
        else:
            self.write(self.body)

    @staticmethod
    def _decompress(data):
        try:
            return zlib.decompress(data, -zlib.MAX_WBITS, 1024 * 1024 * 8)
        except zlib.error:
            print("Error during decompression")
            return b''

    @staticmethod
    def _compress(data):
        return zlib.compress(data, zlib.Z_BEST_COMPRESSION)

