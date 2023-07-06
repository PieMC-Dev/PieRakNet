import time
from pieraknet.packets.online_ping import OnlinePing
from pieraknet.packets.online_pong import OnlinePong


class OnlinePingHandler:
    @staticmethod
    def handle(packet: OnlinePing, server, connection):
        packet.decode()
        new_packet = OnlinePong()
        new_packet.client_timestamp = packet.client_timestamp
        new_packet.server_timestamp = int(time.time())
        new_packet.encode()
        return new_packet.getvalue()
