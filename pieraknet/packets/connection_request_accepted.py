from pieraknet.packets.packet import Packet


class ConnectionRequestAccepted(Packet):
    packet_id = 0x10
    packet_type = 'connection_request_accepted'

    client_address: tuple = None
    system_index: int = None
    internal_ids: list[tuple] = None
    request_time: int = None
    accepted_time: int = None

    def encode_payload(self):
        self.write_address(self.client_address)
        self.write_short(self.system_index)
        for address in self.internal_ids:
            self.write_address(address)
        self.write_long(self.request_time)
        self.write_long(self.accepted_time)
