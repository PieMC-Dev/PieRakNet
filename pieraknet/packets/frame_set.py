from pieraknet.buffer import Buffer

class FrameSet:
    def __init__(self):
        self.sequence_number = 0
        self.frames = []

    def encode(self):
        buf = Buffer()
        buf.write_uint24le(self.sequence_number)

        for frame in self.frames:
            buf.write(frame.encode())

        return buf.getvalue()

    def get_size(self):
        return 3 + sum(frame.get_size() for frame in self.frames)

    def getvalue(self):
        return self.encode()

    def decode(self, data):
        buf = Buffer(data)
        self.sequence_number = buf.read_uint24le()

        while not buf.feos():
            frame = Frame()
            frame.decode(buf)
            self.frames.append(frame)

class Frame:
    def __init__(self):
        self.flags = 0
        self.reliability = 0
        self.fragmented = False
        self.length_bits = 0
        self.reliable_frame_index = 0
        self.sequenced_frame_index = 0
        self.ordered_frame_index = 0
        self.order_channel = 0
        self.compound_size = 0
        self.compound_id = 0
        self.index = 0
        self.body = b''

    def decode(self, buf):
        self.flags = buf.read_byte()
        self.reliability = self.flags >> 5
        self.fragmented = (self.flags & 0x10) != 0
        self.length_bits = buf.read_unsigned_short()

        if self.reliability == 0:
            self.reliable_frame_index = buf.read_uint24le()
        elif self.reliability == 1:  # Add handling for other reliability types
            self.sequenced_frame_index = buf.read_uint24le()
        elif self.reliability == 2:
            self.ordered_frame_index = buf.read_uint24le()
            self.order_channel = buf.read_byte()

        if self.fragmented:
            self.compound_size = buf.read_int()
            self.compound_id = buf.read_short()
            self.index = buf.read_int()

        num_bytes = (self.length_bits + 7) // 8
        self.body = buf.read_bits(self.length_bits)[:num_bytes]
        
    def encode(self):
        buf = Buffer()
        flags = (self.reliability << 5) | (0x10 if self.fragmented else 0)  # Flags: reliability + fragmentation
        body_bits = self.body + [0] * (8 - len(self.body) % 8)  # Pad bits to byte boundary

        buf.write_byte(flags)
        buf.write_unsigned_short(len(body_bits))  # Set body length in bits

        if self.reliability in [1, 2, 3]:
            buf.write_uint24le(self.reliable_frame_index)
        if self.reliability == 1:
            buf.write_uint24le(self.sequenced_frame_index)
        if self.reliability == 2:
            buf.write_uint24le(self.ordered_frame_index)
            buf.write_byte(self.order_channel)
        if self.fragmented:
            buf.write_int(self.compound_size)
            buf.write_short(self.compound_id)
            buf.write_int(self.index)

        num_bytes = (len(body_bits) + 7) // 8
        byte_data = bytearray()
        for i in range(0, len(body_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(body_bits):
                    byte |= body_bits[i + j] << (7 - j)
            byte_data.append(byte)
        buf.write(byte_data)
        
        return buf.getvalue()

    def get_size(self):
        return len(self.encode())

    def getvalue(self):
        return self.encode()