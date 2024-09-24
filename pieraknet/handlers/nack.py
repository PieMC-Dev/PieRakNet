from pieraknet.packets.acknowledgement import Nack

class NackHandler:
    @staticmethod
    def handle(data, server, connection):
        packet = Nack(data)
        packet.decode()

        server.logger.debug(f"Handling NACK for sequence numbers: {packet.sequence_numbers}")

        for sequence_number in packet.sequence_numbers:
            if sequence_number in connection.recovery_queue:
                lost_packet, _ = connection.recovery_queue[sequence_number]
                connection.send_data(lost_packet)

    @staticmethod
    def create_nack_packet(sequence_numbers):
        """ Crea un paquete NACK a partir de una lista de números de secuencia perdidos """
        nack_packet = Nack()
        nack_packet.sequence_numbers = sequence_numbers
        nack_packet.encode()
        return nack_packet.getvalue()