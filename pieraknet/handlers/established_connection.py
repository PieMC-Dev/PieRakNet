from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.ack import AckHandler

class EstablishedConnectionHandler:
    @staticmethod
    def handle(frame, server, connection):
        packet_type = frame.body[0]

        server.logger.debug("Established Connection Packet:")
        server.logger.debug(f"- Packet Type: {packet_type}")
        
        if packet_type == ProtocolInfo.ONLINE_PING:
            connection.process_online_ping(frame)
        elif packet_type == ProtocolInfo.GAME_PACKET:
            connection.process_game_packet(frame)
        elif packet_type == ProtocolInfo.DISCONNECT:
            connection.handle_disconnect(frame.body)
        else:
            connection.process_unknown_packet(frame)
