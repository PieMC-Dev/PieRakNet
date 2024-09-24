from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.disconnect import DisconnectHandler
from pieraknet.handlers.established_connection import EstablishedConnectionHandler

class FrameHandler:
    @staticmethod
    def handle(frame, server, connection):
        server.logger.debug("New Frame:")
        server.logger.debug(f"- Frame Flags: {frame['flags']}")
        server.logger.debug(f"- Frame Body Length: {len(frame['body'])}")

        # Validación de la estructura del frame
        if not (isinstance(frame, dict) and 'flags' in frame and 'body' in frame):
            server.logger.error("Invalid frame structure")
            return

        # Manejo de conexión según el estado
        if not connection.connected:
            connection.handle_connection_requests(frame)
        else:
            EstablishedConnectionHandler.handle(frame, server, connection)

        # Verificación de desconexión
        if frame['body'] and frame['body'][0] == ProtocolInfo.DISCONNECT:
            DisconnectHandler.handle(frame['body'], server, connection)
