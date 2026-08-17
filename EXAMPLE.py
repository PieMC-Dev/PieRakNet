import logging
from pieraknet.server import Server as RakNetServer


class GameInterface:
    def on_game_packet(self, packet_body, connection):
        print("Received game packet:", packet_body)

        # Handle game packets as needed.
        # 0xFE = Minecraft Bedrock game packet.

        if isinstance(packet_body, dict):
            packet_body = packet_body.get("body", b"")

        if isinstance(packet_body, (bytes, bytearray)) and packet_body:
            packet_id = packet_body[0]

            print(f"Game Packet ID: 0x{packet_id:02X}")

            if packet_id == 0xFE:
                print("Received Minecraft 0xFE packet!")
                print(f"Payload: {bytes(packet_body).hex(' ')}")


class BedrockServer:

    def __init__(self):
        self.interface = GameInterface()

        self.server = RakNetServer(
            hostname="0.0.0.0",
            port=19132,
            ipv=4,
            logger=logging,
            game="MCPE",
            name="Python Emulated Server",
            game_protocol_version=2168,
            version_name="1.26.44",
            max_player_count=10,
            modt="Python World",
            game_mode="survival",
            game_mode_number=1,
            portv6=19132
        )

        self.server.interface = self.interface

    def main(self):
        try:
            self.server.response_data = self.server.update_response_data()
            self.server.start()

        except KeyboardInterrupt:
            self.server.stop()

        except Exception:
            logging.exception("Server crashed!")
            self.server.stop()


if __name__ == "__main__":
    server = BedrockServer()
    server.main()
