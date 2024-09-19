class PacketLossHandler:
    @staticmethod
    def handle(incoming_sequence_number, server, connection):
        hole_size = incoming_sequence_number - connection.client_sequence_number
        if hole_size > 0:
            server.logger.debug("Packet Loss Detected:")
            server.logger.debug(f"- Hole Size: {hole_size}")
            connection.nack_queue.extend(range(connection.client_sequence_number + 1, incoming_sequence_number))
