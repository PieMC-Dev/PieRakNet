from pieraknet.packets.packet import Packet

class ConnectionRequest(Packet):
    PACKET_ID = 0x09
    PACKET_TYPE = 'connection_request'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.client_guid: int = None
        self.client_timestamp: int = None

    def decode_payload(self):
        try:
            self.client_guid = self.read_long()
            self.client_timestamp = self.read_long()
        except Exception as e:
            print(f"Error decoding payload: {e}")

    def encode_payload(self):
        try:
            self.write_long(self.client_guid)
            self.write_long(self.client_timestamp)
        except Exception as e:
            print(f"Error encoding payload: {e}")
