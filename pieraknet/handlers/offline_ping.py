from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.packets.offline_pong import OfflinePong

class OfflinePingHandler:
    @staticmethod
    def handle(packet: OfflinePing, server, address: tuple):
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Offline Ping")
        server.logger.debug(f"- Client Timestamp: {packet.client_timestamp}")
        server.logger.debug(f"- MAGIC: {packet.magic}")
        server.logger.debug(f"- Client GUID: {packet.client_guid}")

        new_packet = OfflinePong()
        new_packet.client_timestamp = packet.client_timestamp
        new_packet.server_guid = server.guid
        new_packet.magic = packet.magic  # TODO: server.magic
        new_packet.server_responseData = server.response_data
        new_packet.encode()

        server.send(new_packet.getvalue(), address)

        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {new_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {new_packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Offline Pong")
        server.logger.debug(f"- Client Timestamp: {new_packet.client_timestamp}")
        server.logger.debug(f"- Server GUID: {new_packet.server_guid}")
        server.logger.debug(f"- MAGIC: {new_packet.magic}")
        server.logger.debug(f"- Server Name: {new_packet.server_responseData}")
