from pieraknet.packets.acknowledgement import Nack

class NackHandler:
    @staticmethod
    def handle(data, server, connection):
        packet = Nack(data)
        packet.decode()

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {packet.PACKET_ID}")
        server.logger.debug(f"- Packet Name: NACK")
        server.logger.debug(f"- Sequence Numbers: {packet.sequence_numbers}")

        for sequence_number in packet.sequence_numbers:
            if sequence_number in connection.recovery_queue:
                server.logger.debug(f"Resending lost packet for sequence number {sequence_number}")
                lost_packet = connection.recovery_queue[sequence_number]
                lost_packet.sequence_number = connection.server_sequence_number
                connection.server_sequence_number += 1
                connection.send_data(lost_packet.encode())
