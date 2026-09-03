from pieraknet.server import Server as RakNetServer


class GameInterface:
    def on_game_packet(self, packet_body, connection):
        print("Received game packet:", packet_body)
        # Handle packages as wanted. (0xfe packets)


class BedrockServer:

    def __init__(self):
        self.interface = GameInterface()

        self.server = RakNetServer(
            hostname="0.0.0.0",
            port=19132,
            ipv=4,
            logginglevel = "INFO",
            game_protocol_version=2168,
            version_name="1.26.44"
        )

        self.server.interface = self.interface

    def main(self):
        try:
            self.server.response_data = self.server.update_response_data()
            self.server.start()

        except KeyboardInterrupt:
            self.server.stop()

        except Exception as e:
            self.server.stop()
            raise(e)


if __name__ == "__main__":
    server = BedrockServer()
    server.main()
