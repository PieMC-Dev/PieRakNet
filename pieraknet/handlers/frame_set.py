from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.buffer import Buffer
from pieraknet.handlers.frame import FrameHandler
from pieraknet.handlers.fragmented_frame import FragmentedFrameHandler
from pieraknet.handlers.ack import AckHandler

class FrameSetHandler:
    @staticmethod
    def handle(data, server, connection):
        
        frame_set_packet = FrameSetPacket(server=server)
        #server.logger.debug(f"- Frame set packet: {data}")
        frame_set_packet.decode(Buffer(data))
        incoming_sequence_number = frame_set_packet.sequence_number

        server.logger.debug("New Packet:")
        server.logger.debug(f"- Packet ID: {frame_set_packet.packet_id}")
        server.logger.debug(f"- Packet Name: Frame Set")
        server.logger.debug(f"- Incoming Sequence Number: {incoming_sequence_number}")

        if incoming_sequence_number not in connection.client_sequence_numbers:
            connection.client_sequence_numbers.append(incoming_sequence_number)
            AckHandler.send_ack(server=server, connection=connection, sequence_number=incoming_sequence_number)
            connection.ack_queue.append(incoming_sequence_number)
            connection.handle_packet_loss(incoming_sequence_number)
            connection.client_sequence_number = incoming_sequence_number

            for frame in frame_set_packet.frames:
                #server.logger.info(f"Frame flags: {frame.flags}")

                if frame.flags & 0x08:
                    server.logger.debug("Handling fragmented frame...")
                    FragmentedFrameHandler.handle(frame, server, connection)
                else:
                    server.logger.debug("Handling frame...")
                    FrameHandler.handle(frame, server, connection)