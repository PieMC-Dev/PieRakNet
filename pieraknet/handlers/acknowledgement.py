from pieraknet.packets.acknowledgement import Ack, Nack
from pieraknet.buffer import Buffer

class AckHandler:
    @staticmethod
    def handle(data: bytes, server, connection):
        """Handle received ACK packets."""
        ack_packet = Ack(data)
        ack_packet.decode()

        connection.logger.debug(f"Received ACK for sequence numbers: {ack_packet.sequence_numbers}")

        # Process the acknowledged sequence numbers
        for seq_num in ack_packet.sequence_numbers:
            if seq_num in connection.recovery_queue:
                del connection.recovery_queue[seq_num]
                connection.logger.debug(f"Acknowledged sequence number: {seq_num}")

    @staticmethod
    def send_ack(server, connection, sequence_number):
        """Send an ACK packet for the given sequence number."""
        ack_packet = Ack()
        ack_packet.sequence_numbers = [sequence_number]  # Sending a single ACK for the received sequence number

        ack_packet.encode()  # Ensure this is defined in the Ack class
        connection.send_data(ack_packet.getvalue())  # Send the ACK
        server.logger.debug(f"ACK sent for sequence number: {sequence_number}")

class NackHandler:
    @staticmethod
    def handle(data: bytes, server, connection):
        """ Handle received NACK packets. """
        nack_packet = Nack(data)
        nack_packet.decode()

        connection.logger.debug(f"Received NACK for sequence numbers: {nack_packet.sequence_numbers}")
        
        # Handle the negative acknowledgment (e.g., request retransmission)
        for seq_num in nack_packet.sequence_numbers:
            connection.logger.debug(f"Requesting retransmission for sequence number: {seq_num}")
            connection.nack_queue.append(seq_num)  # Add to NACK queue for retransmission
