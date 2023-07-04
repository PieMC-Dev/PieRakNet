from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.packets.offline_pong import OfflinePong


class OfflinePingHandler:
    @staticmethod
    def handle(packet: OfflinePing, server, address: tuple):
        packet.decode()
        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {str(packet.getvalue()[0])}")
        server.logger.debug(f"- Packet Body: {str(packet.getvalue()[1:])}")
        server.logger.debug(f"- Packet Name: Offline Ping")
        server.logger.debug(f"- Client Timestamp: {str(packet.client_timestamp)}")
        server.logger.debug(f"- MAGIC: {str(packet.magic)}")
        server.logger.debug(f"- Client GUID: {str(packet.client_guid)}")
        new_packet = OfflinePong()
        new_packet.client_timestamp = packet.client_timestamp
        new_packet.server_guid = server.guid
        new_packet.magic = packet.magic  # TODO: server.magic
        new_packet.server_name = server.name
        new_packet.encode()
        server.send(new_packet.getvalue(), address)
        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {str(new_packet.getvalue()[0])}")
        server.logger.debug(f"- Packet Body: {str(new_packet.getvalue()[1:])}")
        server.logger.debug(f"- Packet Name: Offline Pong")
        server.logger.debug(f"- Client Timestamp: {str(new_packet.client_timestamp)}")
        server.logger.debug(f"- Server GUID: {str(new_packet.server_guid)}")
        server.logger.debug(f"- MAGIC: {str(new_packet.magic)}")
        server.logger.debug(f"- Server Name: {str(new_packet.server_name)}")
