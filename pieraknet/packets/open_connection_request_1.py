from pieraknet.packets.packet import Packet

class OpenConnectionRequest1(Packet):
    PACKET_ID = 0x05
    PACKET_TYPE = 'open_connection_request_1'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.magic: bytes = None
        self.raknet_protocol_version: int = None
        self.mtu_size: int = None

    def decode_payload(self):
        self.magic = self.read_magic()
        self.raknet_protocol_version = int(self.read_byte())
        # Asegurarse de que el valor se pueda convertir a entero correctamente
        try:
            self.mtu_size = len(self.read()) + 46
        except ValueError:
            self.mtu_size = None
