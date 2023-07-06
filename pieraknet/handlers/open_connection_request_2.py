from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.packets.open_connection_reply_2 import OpenConnectionReply2
from pieraknet.connection import Connection


class OpenConnectionRequest2Handler:
    @staticmethod
    def handle(packet: OpenConnectionRequest2, server, address: tuple):
        packet.decode()
        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {str(packet.getvalue()[0])}")
        server.logger.debug(f"- Packet Body: {str(packet.getvalue()[1:])}")
        server.logger.debug(f"- Packet Name: Open Connection Request 2")
        server.logger.debug(f"- MAGIC: {str(packet.magic)}")
        server.logger.debug(f"- Server Address: {str(packet.server_address)}")
        server.logger.debug(f"- MTU Size: {str(packet.mtu_size)}")
        server.logger.debug(f"- Client GUID: {str(packet.client_guid)}")

        new_packet = OpenConnectionReply2()
        new_packet.magic = packet.magic  # TODO: server.magic
        new_packet.server_guid = server.guid
        new_packet.client_address = address
        new_packet.mtu_size = packet.mtu_size
        new_packet.encode()

        server.send(new_packet.getvalue(), address)

        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {str(new_packet.getvalue()[0])}")
        server.logger.debug(f"- Packet Body: {str(new_packet.getvalue()[1:])}")
        server.logger.debug(f"- Packet Name: Open Connection Reply 2")
        server.logger.debug(f"- MAGIC: {str(new_packet.magic)}")
        server.logger.debug(f"- Server GUID: {str(new_packet.server_guid)}")
        server.logger.debug(f"- Client Address: {str(new_packet.client_address)}")
        server.logger.debug(f"- MTU Size: {str(new_packet.mtu_size)}")

        connection = Connection(address, server, packet.mtu_size, packet.client_guid)
        server.add_connection(connection)
