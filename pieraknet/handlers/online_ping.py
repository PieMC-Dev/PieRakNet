from pieraknet.packets.online_ping import OnlinePing
from pieraknet.packets.online_pong import OnlinePong
from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.buffer import Buffer
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

    def create_online_ping(server, connection):
        new_ping = OnlinePing()
        new_ping.client_timestamp = int(time.time() * 1000)
        new_ping.encode()
        OnlinePingPacket = new_ping.getvalue()

        frame_set_packet = FrameSetPacket(server)
        frame_set_packet.sequence_number = connection.server_sequence_number
        frame_set_packet.create_frame(OnlinePingPacket, flags=0x00)

        # Codificar y enviar directamente sin usar Buffer
        connection.send_data(frame_set_packet.encode()) 
    
    def process_online_ping(frame, server, connection):

        OnlinePingPacket = OnlinePing(frame['body'])

        OnlinePongPacket = OnlinePingHandler.handle(OnlinePingPacket, server)

        frame_set_packet = FrameSetPacket(server)
        frame_set_packet.sequence_number = connection.server_sequence_number
        frame_set_packet.create_frame(OnlinePongPacket, flags=0x00)

        # Codificar y enviar directamente sin usar Buffer
        connection.send_data(frame_set_packet.encode())
