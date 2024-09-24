class GamePacketHandler:
    @staticmethod
    def handle(frame_body, server, connection):
        server.logger.debug("Game Packet:")
        server.logger.debug(f"- Packet Body Length: {len(frame_body)}")

        if hasattr(server, "interface") and hasattr(server.interface, "on_game_packet"):
            server.interface.on_game_packet(frame_body, connection)
