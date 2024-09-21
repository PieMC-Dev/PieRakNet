from pieraknet.server import Server as RakNetServer

class BedrockServer:

    def main(self):
        interface = GameInterface()
        server = RakNetServer(logginglevel = "INFO")
        server.interface = interface

        server.start()

if __name__ == '__main__':
    server = BedrockServer()
    server.main()


class GameInterface:
    def on_game_packet(self, packet_body, connection):
        print("Received game packet:", packet_body)
        # Handle packages as wanted. (0xfe packets)