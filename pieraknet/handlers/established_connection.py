from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.online_ping import OnlinePingHandler
from pieraknet.handlers.game_packet import GamePacketHandler
from pieraknet.handlers.disconnect import DisconnectHandler
from pieraknet.handlers.unknown_packet import UnknownPacketHandler

class EstablishedConnectionHandler:
    @staticmethod
    def handle(frame, server, connection):
        packet_type = frame['body'][0]

        server.logger.debug("Established Connection Packet:")
        server.logger.debug(f"- Packet Type: {packet_type}")
        
        if packet_type == ProtocolInfo.ONLINE_PING:
            OnlinePingHandler.process_online_ping(frame, server, connection)
        elif packet_type == ProtocolInfo.GAME_PACKET:
            GamePacketHandler.handle(frame, server, connection)
        elif packet_type == ProtocolInfo.DISCONNECT:
            DisconnectHandler.handle(frame['body'], server, connection)
        else:
            UnknownPacketHandler.handle(frame['body'], server, connection)
