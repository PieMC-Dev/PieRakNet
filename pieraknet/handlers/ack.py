from pieraknet.packets.acknowledgement import Ack

class AckHandler:
    @staticmethod
    def handle(data, server, connection):
        packet = Ack(data)
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Name: ACK")
        server.logger.debug(f"- Sequence Numbers: {packet.sequence_numbers}")

        for sequence_number in packet.sequence_numbers:
            connection.recovery_queue.pop(sequence_number, None)
