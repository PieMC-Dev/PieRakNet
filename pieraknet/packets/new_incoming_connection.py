from pieraknet.packets.packet import Packet


class NewIncomingConnection(Packet):
    packet_id = 0x13
    packet_type = 'new_incoming_connection'

    server_address: tuple = None
    internal_address: tuple = None # ('255.255.255.255', 19132)

    def encode_payload(self):
        self.write_address(self.server_address)
        self.write_address(self.internal_address)

    def decode_payload(self):
        self.server_address = self.read_address()
        self.internal_address = self.read_address()
