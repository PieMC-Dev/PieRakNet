from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.packets.open_connection_reply_2 import OpenConnectionReply2
from pieraknet.connection import Connection

class OpenConnectionRequest2Handler:
    @staticmethod
    def handle(packet: OpenConnectionRequest2, server, address: tuple):
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Open Connection Request 2")
        server.logger.debug(f"- MAGIC: {packet.magic}")
        server.logger.debug(f"- Server Address: {packet.server_address}")
        server.logger.debug(f"- MTU Size: {packet.mtu_size}")
        server.logger.debug(f"- Client GUID: {packet.client_guid}")

        new_packet = OpenConnectionReply2()
        new_packet.magic = packet.magic  # TODO: server.magic
        new_packet.server_guid = server.guid
        new_packet.client_address = address
        new_packet.encryption_enabled = False
        new_packet.mtu_size = packet.mtu_size
        new_packet.encode()

        server.send(new_packet.getvalue(), address)

        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {new_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {new_packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Open Connection Reply 2")
        server.logger.debug(f"- MAGIC: {new_packet.magic}")
        server.logger.debug(f"- Server GUID: {new_packet.server_guid}")
        server.logger.debug(f"- Client Address: {new_packet.client_address}")
        server.logger.debug(f"- MTU Size: {new_packet.mtu_size}")

        connection = Connection(address, server, packet.mtu_size, packet.client_guid)
        server.add_connection(connection)
