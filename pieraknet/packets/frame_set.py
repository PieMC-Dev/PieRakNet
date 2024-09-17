from pieraknet.buffer import Buffer

class Frame:
    def __init__(self, flags=0, length_bits=0, reliable_index=0, ordered_index=0, index=0, body=b''):
        self.flags = flags
        self.length_bits = length_bits
        self.reliable_index = reliable_index
        self.ordered_index = ordered_index
        self.index = index
        self.body = body

    def encode(self):
        buffer = Buffer()
        buffer.write_byte(self.flags)
        buffer.write_unsigned_short(self.length_bits)

        if self.flags & 0x02:  # Reliable
            buffer.write_uint24le(self.reliable_index)
        if self.flags & 0x04:  # Ordered
            buffer.write_uint24le(self.ordered_index)

        buffer.write_byte(self.index)
        buffer.write(self.body)
        return buffer.getvalue()

    @staticmethod
    def decode(data):
        buffer = Buffer(data)
        flags = buffer.read_byte()
        length_bits = buffer.read_unsigned_short()

        reliable_index = ordered_index = index = 0
        if flags & 0x02:  # Reliable
            reliable_index = buffer.read_uint24le()
        if flags & 0x04:  # Ordered
            ordered_index = buffer.read_uint24le()

        index = buffer.read_byte()
        body = buffer.read((length_bits + 7) // 8)
        
        return Frame(flags, length_bits, reliable_index, ordered_index, index, body)

class FrameSetPacket:
    def __init__(self, packet_id, sequence_number):
        self.packet_id = packet_id
        self.sequence_number = sequence_number
        self.frames = []

    def encode(self):
        buffer = Buffer()
        buffer.write_byte(self.packet_id)
        buffer.write_uint24le(self.sequence_number)
        
        for frame in self.frames:
            encoded_frame = frame.encode()
            buffer.write(encoded_frame)
        
        return buffer.getvalue()

    @staticmethod
    def decode(data):
        buffer = Buffer(data)
        packet_id = buffer.read_byte()
        sequence_number = buffer.read_uint24le()

        frames = []
        while buffer.remaining() > 0:
            # Assuming frame data can be variable length, read until the buffer is exhausted
            frame = Frame.decode(buffer.read_remaining())
            frames.append(frame)

        packet = FrameSetPacket(packet_id, sequence_number)
        packet.frames = frames
        return packet
