from pieraknet.packets.packet import Packet


class OfflinePong(Packet):
    packet_id = 0x1c
    packet_type = 'offline_pong'

    client_timestamp: int = None
    server_guid: int = None
    magic: bytes = None
    server_name: str = None

    def encode_payload(self):
        self.write_long(self.client_timestamp)
        self.write_long(self.server_guid)

        if not isinstance(self.magic, bytes):
            self.magic = str(self.magic)
            self.magic = self.magic.encode()


        self.write_magic(self.magic)
        if not isinstance(self.server_name, bytes):
            self.server_name: bytes = self.server_name.encode('utf-8')
        self.write_string(self.server_name)

