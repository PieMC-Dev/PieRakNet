from pieraknet.packets.frame_set import FrameSetPacket  # Asumiendo que el FrameSetPacket está en esta ruta

class FragmentedFrameHandler:
    @staticmethod
    def handle(frame, server, connection):
        server.logger.debug("New Fragmented Frame:")
        server.logger.debug(f"- Compound ID: {frame['compound_id']}")
        server.logger.debug(f"- Index: {frame['index']}")
        server.logger.debug(f"- Compound Size: {frame['compound_size']}")

        fragments = connection.fragmented_packets.setdefault(frame['compound_id'], {})
        fragments[frame['index']] = frame

        if len(fragments) == frame['compound_size']:
            server.logger.debug("Reassembling fragmented frame:")
            body = b''.join(fragments[i]['body'] for i in range(frame['compound_size']))
            new_frame = {
                'flags': 0,
                'length_in_bits': len(body) * 8,
                'body': body,
                'reliable_frame_index': 0,
                'sequenced_frame_index': 0,
                'ordered_frame_index': 0,
                'order_channel': 0,
                'compound_size': 0,
                'compound_id': 0,
                'index': 0
            }
            del connection.fragmented_packets[frame['compound_id']]
            connection.handle_frame(new_frame)  # Asegúrate de que esta función acepte un diccionario
