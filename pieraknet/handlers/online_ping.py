from pieraknet.packets.online_ping import OnlinePing
from pieraknet.packets.online_pong import OnlinePong
import time

class OnlinePingHandler:
    @staticmethod
    def handle(packet: OnlinePing, server):
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Name: Online Ping")
        server.logger.debug(f"- Client Timestamp: {packet.client_timestamp}")

        new_packet = OnlinePong()
        new_packet.client_timestamp = packet.client_timestamp
        new_packet.server_timestamp = int(time.time() * 1000)

        new_packet.encode()
        return new_packet.getvalue()
