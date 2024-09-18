import time
from pieraknet.packets.connection_request import ConnectionRequest
from pieraknet.packets.connection_request_accepted import ConnectionRequestAccepted

class ConnectionRequestHandler:
    @staticmethod
    def handle(packet: bytes, server, connection):
        request_packet = ConnectionRequest(packet)
        request_packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {request_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {request_packet.getvalue()}")
        server.logger.debug(f"- Packet Name: Connection Request")
        server.logger.debug(f"- Client Timestamp: {request_packet.client_timestamp}")
        server.logger.debug(f"- Client GUID: {request_packet.client_guid}")

        new_packet = ConnectionRequestAccepted()
        new_packet.client_address = connection.address
        new_packet.system_index = 0
        new_packet.internal_ids = [('255.255.255.255', 19132)] * 10
        new_packet.request_time = request_packet.client_timestamp
        new_packet.accepted_time = int(time.time() * 1000)
        new_packet.encode()

        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {new_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {new_packet.getvalue()}")
        server.logger.debug(f"- Packet Name: Connection Request Accepted")
        server.logger.debug(f"- Client Client Address: {new_packet.client_address}")
        server.logger.debug(f"- Packet Index: {new_packet.system_index}")
        server.logger.debug(f"- Internal Ids: {new_packet.internal_ids}")
        server.logger.debug(f"- Request Time: {new_packet.request_time}")
        server.logger.debug(f"- Accepted Time: {new_packet.accepted_time}")

        return new_packet.getvalue()