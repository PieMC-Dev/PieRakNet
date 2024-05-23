from pieraknet.packets.packet import Packet

class NewIncomingConnection(Packet):
    PACKET_ID = 0x13
    PACKET_TYPE = 'new_incoming_connection'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.server_address: tuple = None
        self.client_address: tuple = None  # Internal client address ('255.255.255.255', 19132)

    def encode_payload(self):
        self.write_address(self.server_address)
        self.write_address(self.client_address)

    def decode_payload(self):
        self.server_address = self.read_address()
        self.client_address = self.read_address()
