from pieraknet.packets.acknowledgement import Nack

class NackHandler:
    @staticmethod
    def handle(data, server, connection):
        packet = Nack(data)
        packet.decode()

        server.logger.debug(f"Handling NACK for sequence numbers: {packet.sequence_numbers}")

        for sequence_number in packet.sequence_numbers:
            if sequence_number in connection.recovery_queue:
                lost_packet = connection.recovery_queue[sequence_number]
                lost_packet.sequence_number = connection.server_sequence_number
                connection.server_sequence_number += 1
                connection.send_data(lost_packet.encode())
