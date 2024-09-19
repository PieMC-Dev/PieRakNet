class DisconnectHandler:
    @staticmethod
    def handle(data, server, connection):
        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet Name: DISCONNECT")
        server.logger.debug(f"- Packet Body: {data}")

        connection.disconnect()
