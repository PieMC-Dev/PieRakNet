from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.buffer import Buffer

class FrameSetHandler:
    @staticmethod
    def handle(data, server, connection):
        frame_set_packet = FrameSetPacket(server=server)
        frame_set_packet.decode(Buffer(data))
        incoming_sequence_number = frame_set_packet.sequence_number

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {frame_set_packet.packet_id}")
        server.logger.debug(f"- Packet Name: Frame Set")
        server.logger.debug(f"- Incoming Sequence Number: {incoming_sequence_number}")

        if incoming_sequence_number not in connection.client_sequence_numbers:
            connection.client_sequence_numbers.append(incoming_sequence_number)
            connection.ack_queue.append(incoming_sequence_number)
            connection.handle_packet_loss(incoming_sequence_number)
            connection.client_sequence_number = incoming_sequence_number

            for frame in frame_set_packet.frames:
                if frame.flags & 0x01:
                    connection.handle_fragmented_frame(frame)
                else:
                    connection.handle_frame(frame)