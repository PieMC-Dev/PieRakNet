from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.packets.open_connection_reply_2 import OpenConnectionReply2


class OpenConnectionRequest2Handler:
    @staticmethod
    def handle(packet: OpenConnectionRequest2, server, address: tuple):
        packet.decode()

        new_packet = OpenConnectionReply2()
        new_packet.magic = packet.magic # TODO: server.magic
        new_packet.server_guid = server.guid
        new_packet.client_address = address
        new_packet.mtu_size = packet.mtu_size
        new_packet.encode()

        server.send(new_packet.getvalue(), address)
