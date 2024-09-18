from pieraknet.packets.frame_set import Frame

class FragmentedFrameHandler:
    @staticmethod
    def handle(frame, server, connection):
        server.logger.debug("New Fragmented Frame:")
        server.logger.debug(f"- Compound ID: {frame.compound_id}")
        server.logger.debug(f"- Index: {frame.index}")
        server.logger.debug(f"- Compound Size: {frame.compound_size}")

        fragments = connection.fragmented_packets.setdefault(frame.compound_id, {})
        fragments[frame.index] = frame

        if len(fragments) == frame.compound_size:
            server.logger.debug("Reassembling fragmented frame:")
            server.logger.debug(f"- Compound ID: {frame.compound_id}")

            body = b''.join(fragments[i].body for i in range(frame.compound_size))
            new_frame = Frame(flags=0, length_bits=0, body=body)
            del connection.fragmented_packets[frame.compound_id]
            connection.handle_frame(new_frame)
