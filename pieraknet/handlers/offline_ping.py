from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.packets.offline_pong import OfflinePong


class OfflinePingHandler:
    @staticmethod
    def handle(packet: OfflinePing, server, address: tuple):
        packet.decode()
        new_packet = OfflinePong()
        new_packet.client_timestamp = packet.client_timestamp
        new_packet.server_guid = server.guid
        new_packet.magic = packet.magic  # TODO: server.magic
        new_packet.server_name = server.name
        new_packet.encode()
        server.send(new_packet.getvalue(), address)
