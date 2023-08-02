import time
from pieraknet.packets.connection_request import ConnectionRequest
from pieraknet.packets.connection_request_accepted import ConnectionRequestAccepted


class ConnectionRequestHandler:
    @staticmethod
    def handle(packet: bytes, server, connection):
        packet = ConnectionRequest(packet)
        packet.decode()
        new_packet = ConnectionRequestAccepted()
        new_packet.client_address = connection.address
        new_packet.system_index = 0
        new_packet.internal_ids = [('255.255.255.255', 19132)] * 10
        new_packet.request_time = packet.client_timestamp
        new_packet.accepted_time = int(time.time())
        new_packet.encode()
        return new_packet.getvalue()
