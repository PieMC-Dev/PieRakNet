from pieraknet.packets.new_incoming_connection import NewIncomingConnection

class NewIncomingConnectionHandler:
    @staticmethod
    def handle(frame_body, server, connection):
        try:
            packet = NewIncomingConnection(server, frame_body)
            packet.decode()

            server.logger.debug("New Packet:")
            server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
            server.logger.debug(f"- Packet Name: New Incoming Connection")
            server.logger.debug(f"- Server Address: {packet.server_address}")

            if packet.server_address[1] == server.port:
                connection.connected = True
                server.logger.debug(f"Connection established with {connection.address}")

                if hasattr(server, "interface") and hasattr(server.interface, "on_new_incoming"):
                    server.interface.on_new_incoming(connection)

        except Exception as e:
            server.logger.error(f"Error decoding New Incoming Connection packet: {e}")
