from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.disconnect import DisconnectHandler
from pieraknet.packets.frame import Frame
from pieraknet.handlers.established_connection import EstablishedConnectionHandler

class FrameHandler:
    @staticmethod
    def handle(frame: Frame, server, connection):
        server.logger.debug("New Frame:")
        server.logger.debug(f"- Frame Flags: {frame.flags}")
        server.logger.debug(f"- Frame Body Length: {len(frame.body)}")

        if not (hasattr(frame, 'flags') and hasattr(frame, 'body')):
            server.logger.error("Invalid packet structure")
            return

        if not connection.connected:
            connection.handle_connection_requests(frame)
        else:
            EstablishedConnectionHandler.handle(frame, server, connection)

        if frame.body[0] == ProtocolInfo.DISCONNECT:
            DisconnectHandler.handle(frame.body, server, connection)

