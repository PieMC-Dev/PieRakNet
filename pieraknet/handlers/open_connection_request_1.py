from pieraknet.packets.open_connection_request_1 import OpenConnectionRequest1
from pieraknet.packets.open_connection_reply_1 import OpenConnectionReply1
from pieraknet.packets.incompatible_protocol import IncompatibleProtocol

class OpenConnectionRequest1Handler:
    @staticmethod
    def handle(packet: OpenConnectionRequest1, server, address: tuple):
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {packet.getvalue()[1:]}")
        server.logger.debug(f"- Packet Name: Open Connection Request 1")
        server.logger.debug(f"- MAGIC: {packet.magic}")
        server.logger.debug(f"- Protocol Version: {packet.raknet_protocol_version}")
        server.logger.debug(f"- MTU size: {packet.mtu_size}")

        if packet.raknet_protocol_version == server.raknet_protocol_version:
            new_packet = OpenConnectionReply1()
            new_packet.magic = packet.magic
            new_packet.server_guid = server.guid
            new_packet.use_security = False
            new_packet.mtu_size = packet.mtu_size
        else:
            new_packet = IncompatibleProtocol()
            new_packet.raknet_protocol_version = server.raknet_protocol_version
            new_packet.magic = packet.magic  # TODO: server.magic
            new_packet.server_guid = server.guid

        new_packet.encode()
        server.send(new_packet.getvalue(), address)

        server.logger.debug("Sent Packet:")
        server.logger.debug(f"- Packet ID: {new_packet.PACKET_ID}")
        server.logger.debug(f"- Packet Body: {new_packet.getvalue()[1:]}")

        if new_packet.PACKET_TYPE == 'open_connection_reply_1':
            server.logger.debug(f"- Packet Name: Open Connection Reply 1")
            server.logger.debug(f"- MAGIC: {new_packet.magic}")
            server.logger.debug(f"- Server GUID: {new_packet.server_guid}")
            server.logger.debug(f"- Use Security: {new_packet.use_security}")
            server.logger.debug(f"- MTU Size: {new_packet.mtu_size}")
        elif new_packet.PACKET_TYPE == 'incompatible_protocol':
            server.logger.debug(f"- Packet Name: Incompatible Protocol")
            server.logger.debug(f"- Protocol Version: {new_packet.magic}")
            server.logger.debug(f"- MAGIC: {new_packet.magic}")
            server.logger.debug(f"- Server: {new_packet.magic}")
        else:
            server.logger.critical(f"WTF?! Error: OCR1H - Invalid Sent Packet Type ({new_packet.PACKET_TYPE}).")
