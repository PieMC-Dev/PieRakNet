from pieraknet.packets.open_connection_request_1 import OpenConnectionRequest1
from pieraknet.packets.open_connection_reply_1 import OpenConnectionReply1
from pieraknet.packets.incompatible_protocol import IncompatibleProtocol


class OpenConnectionRequest1Handler:
    @staticmethod
    def handle(packet: OpenConnectionRequest1, server, address: tuple):
        packet.decode()
        if packet.protocol_version == server.protocol_version:
            new_packet = OpenConnectionReply1()
            new_packet.magic = packet.magic
            new_packet.server_guid = server.guid
            new_packet.use_security = False
            new_packet.mtu_size = packet.mtu_size
        else:
            new_packet = IncompatibleProtocol()
            new_packet.raknet_version = server.protocol_version
            new_packet.magic = packet.magic  # TODO: server.magic
            new_packet.server_guid = server.guid
        new_packet.encode()
        server.send(new_packet.getvalue(), address)
