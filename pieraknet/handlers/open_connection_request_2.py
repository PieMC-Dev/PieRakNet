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
        new_packet.magic = packet.magic
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

        # Initialize the Connection with server and address
        connection = Connection(server, address)
        server.add_connection(connection)

# 08:50:07 [PieRakNet - DEBUG] - Sent Packet:
# 08:50:07 [PieRakNet - DEBUG] - - Packet ID: 8
# 08:50:07 [PieRakNet - DEBUG] - - Packet Body: b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\x11\x92\xa2\r\xc4\r\n;\x04?W\xfd\xa8\x9c\xb4\x05\xd4\x00'
# 08:50:07 [PieRakNet - DEBUG] - - Packet Name: Open Connection Reply 2
# 08:50:07 [PieRakNet - DEBUG] - - MAGIC: b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx'
# 08:50:07 [PieRakNet - DEBUG] - - Server GUID: 1266252625251994171
# 08:50:07 [PieRakNet - DEBUG] - - Client Address: ('192.168.2.87', 40116)
# 08:50:07 [PieRakNet - DEBUG] - - MTU Size: 1492

# Clent address: \x04?W\xfd\xa8\x9c\xb4
# System index: \x00\x00
# Internal IDs: \x04\x00\x00\x00\x00J\xbc
# Request time: \x00\x00\x00\x00\x00\x05\x7fT
# Time: \x00\x00\x01\x92\t\x0b\x95\x88
#  b'\x04?W\xfd\xa8\x9c\xb4\x00\x00\x04\x00\x00\x00\x00J\xbc\x00\x00\x00\x00\x00\x05\x7fT\x00\x00\x01\x92\t\x0b\x95\x88'