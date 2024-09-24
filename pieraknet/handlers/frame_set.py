from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.buffer import Buffer
from pieraknet.handlers.frame import FrameHandler
from pieraknet.handlers.fragmented_frame import FragmentedFrameHandler
from pieraknet.handlers.acknowledgement import AckHandler

class FrameSetHandler:
    @staticmethod
    def handle(data: bytes, server, connection):
        frame_set_packet = FrameSetPacket(server)
        frame_set_packet.decode(data)
        incoming_sequence_number = frame_set_packet.sequence_number

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {frame_set_packet.packet_id}")
        server.logger.debug(f"- Packet Name: Frame Set")
        server.logger.debug(f"- Incoming Sequence Number: {incoming_sequence_number}")

        # Process if the sequence number has not been processed
        if incoming_sequence_number not in connection.client_sequence_numbers:
            connection.client_sequence_numbers.add(incoming_sequence_number)

            # Send ACK for the received sequence number
            AckHandler.send_ack(server=server, connection=connection, sequence_number=incoming_sequence_number)
            connection.ack_queue.append(incoming_sequence_number)

            # Update the client sequence number
            connection.client_sequence_number = incoming_sequence_number

            # Process each frame in the packet
            for frame in frame_set_packet.frames:
                FrameSetHandler.process_frame(frame, server, connection)

    @staticmethod
    def process_frame(frame, server, connection):
        if frame['flags'] & 0x08:  # Check if it's a fragmented frame
            server.logger.debug("Handling fragmented frame...")
            FragmentedFrameHandler.handle(frame, server, connection)
        else:
            server.logger.debug("Handling frame...")
            FrameHandler.handle(frame, server, connection)
