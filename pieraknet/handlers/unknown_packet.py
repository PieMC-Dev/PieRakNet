class UnknownPacketHandler:
    @staticmethod
    def handle(frame_body, server, connection):
        server.logger.debug("Unknown Packet:")
        server.logger.debug(f"- Packet Body Length: {len(frame_body)}")

        if hasattr(server, "interface") and hasattr(server.interface, "on_unknown_packet"):
            server.interface.on_unknown_packet(frame_body, connection)
