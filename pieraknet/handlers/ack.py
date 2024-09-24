from pieraknet.packets.acknowledgement import Ack
from pieraknet.protocol_info import ProtocolInfo

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
            
    @staticmethod
    def create_ack_packet(sequence_numbers):
        """ Crea un paquete ACK a partir de una lista de números de secuencia """
        ack_packet = Ack()
        ack_packet.sequence_numbers = sequence_numbers
        ack_packet.encode()
        return ack_packet.getvalue()
    
    @staticmethod
    def send_ack(server, connection, sequence_number):
        ack_packet = Ack()
        ack_packet.sequence_numbers = [sequence_number]
        ack_packet.encode()
        
        server.send(ack_packet.getvalue(), connection.address)
        server.logger.debug(f"Sent ACK for sequence number {sequence_number}")
