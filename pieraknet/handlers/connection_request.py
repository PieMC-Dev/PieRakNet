from pieraknet.packets.connection_request import ConnectionRequest
from pieraknet.packets.connection_request_accepted import ConnectionRequestAccepted

class ConnectionRequestHandler:
    # Example packet: b'\t\xb3\xde\x85\x0fBa~.\x00\x00\x00\x00\x00\x12\xbd\x8d\x00'
    @staticmethod
    def handle(frame_body, server, connection):
        # Decode the incoming Connection Request packet
        packet = ConnectionRequest(frame_body)
        packet.decode()

        server.logger.debug("New Packet Received:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {packet.getvalue()}")
        server.logger.debug(f"- Packet Name: Connection Request")
        server.logger.debug(f"- Client Timestamp: {packet.client_timestamp}")
        server.logger.debug(f"- Client GUID: {packet.client_guid}")
        
        # Create and encode a Connection Request Accepted packet
        new_packet = ConnectionRequestAccepted()
        new_packet.client_address = connection.address
        new_packet.system_index = server.raknet_protocol_version
        new_packet.internal_ids = [('255.255.255.255', 19132)] * 10
        new_packet.request_time = packet.client_timestamp
        new_packet.accepted_time = 0

        server.logger.debug("Sending Packet:")
        server.logger.debug(f"- Packet ID: {new_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {new_packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Connection Request Accepted")
        server.logger.debug(f"- Client Client Address: {new_packet.client_address}")
        server.logger.debug(f"- Packet Index: {new_packet.system_index}")
        server.logger.debug(f"- Internal Ids: {new_packet.internal_ids}")
        server.logger.debug(f"- Request Time: {new_packet.request_time}")
        server.logger.debug(f"- Accepted Time: {new_packet.accepted_time}")

        new_packet.encode()
        return new_packet.getvalue()