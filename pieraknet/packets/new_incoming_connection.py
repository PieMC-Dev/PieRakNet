from pieraknet.packets.packet import Packet

class NewIncomingConnection(Packet):
    PACKET_ID = 0x13
    PACKET_TYPE = 'new_incoming_connection'

    def __init__(self, server, data: bytes = b''):
        super().__init__(data)
        self.server_address: tuple = [(server.hostname, server.port)]
        self.client_address: tuple = [('255.255.255.255', 19132)] * 20
        self.timestamp: int = 0
        self.server_timestamp: int = 0

    def encode_payload(self):
        self.write_address(self.server_address)
        self.write_address(self.client_address)
        self.write_long(self.timestamp)
        self.write_long(self.server_timestamp)

    def decode_payload(self):
        self.server_address = self.read_address()
        self.client_address = self.read_address()
        self.timestamp = self.read_long()
        self.server_timestamp = self.read_long()
