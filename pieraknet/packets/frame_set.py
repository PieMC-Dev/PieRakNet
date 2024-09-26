from pieraknet.buffer import Buffer
from pieraknet.packets.packet import Packet
from pieraknet.protocol_info import ProtocolInfo

class FrameSetPacket(Packet):
    def __init__(self, server=None, data: bytes = b''):
        super().__init__(data)
        self.server = server
        self.packet_id = ProtocolInfo.FRAME_SET
        self.sequence_number = 0
        self.frames = []

    def decode(self, data):
        buffer = Buffer(data)
        self.packet_id = buffer.read_byte()
        self.sequence_number = buffer.read_uint24le()

        while not buffer.feos():
            frame = self.decode_frame(buffer)
            self.frames.append(frame)

    def decode_frame(self, buffer):

        frame = {
            'flags': buffer.read_byte(),
            'length_in_bits': buffer.read_unsigned_short(),
            'reliable_frame_index': 0,
            'sequenced_frame_index': 0,
            'ordered_frame_index': 0,
            'order_channel': 0,
            'compound_size': 0,
            'compound_id': 0,
            'index': 0,
            'body': b''
        }

        reliability_type = (frame['flags'] >> 5) & 0x07
        is_fragmented = (frame['flags'] >> 4) & 0x01

        if reliability_type in {2, 3, 4, 6, 7}:
            frame['reliable_frame_index'] = buffer.read_uint24le()

        if reliability_type in {1, 4}:
            frame['sequenced_frame_index'] = buffer.read_uint24le()

        if reliability_type in {1, 3, 4, 7}:
            frame['ordered_frame_index'] = buffer.read_uint24le()
            frame['order_channel'] = buffer.read_byte()

        if is_fragmented:
            frame['compound_size'] = buffer.read_int()
            frame['compound_id'] = buffer.read_short()
            frame['index'] = buffer.read_int()

        body_length = (frame['length_in_bits'] + 7) // 8
        frame['body'] = buffer.read(body_length)

        return frame

    def encode(self):
        buffer = Buffer()
        buffer.write_byte(self.packet_id)
        buffer.write_uint24le(self.sequence_number)

        for frame in self.frames:
            self.encode_frame(buffer, frame)

        return buffer.getvalue()

    def encode_frame(self, buffer, frame):
        buffer.write_byte(frame['flags'])
        buffer.write_unsigned_short(frame['length_in_bits'])

        reliability_type = (frame['flags'] >> 5) & 0x07
        is_fragmented = (frame['flags'] >> 4) & 0x01

        if reliability_type in {2, 3, 4, 6, 7}:
            buffer.write_uint24le(frame['reliable_frame_index'])

        if reliability_type in {1, 4}:
            buffer.write_uint24le(frame['sequenced_frame_index'])

        if reliability_type in {1, 3, 4, 7}:
            buffer.write_uint24le(frame['ordered_frame_index'])
            buffer.write_byte(frame['order_channel'])

        if is_fragmented:
            buffer.write_int(frame['compound_size'])
            buffer.write_short(frame['compound_id'])
            buffer.write_int(frame['index'])

        buffer.write(frame['body'])

    def create_frame(self, body: bytes, flags: int = 0):
        frame = {
            'flags': flags,
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
        self.frames.append(frame)

    def set_sequence_number(self, sequence_number: int):
        self.sequence_number = sequence_number