from pieraknet.buffer import Buffer
from pieraknet.packets.acknowledgement import Ack

class Frame:
    def __init__(self, flags, length_bits, reliable_index=None, sequenced_index=None, ordered_index=None, 
                 order_channel=None, compound_size=None, compound_id=None, index=None, body=b''):
        self.flags = flags
        self.length_bits = length_bits
        self.reliable_index = reliable_index
        self.sequenced_index = sequenced_index
        self.ordered_index = ordered_index
        self.order_channel = order_channel
        self.compound_size = compound_size
        self.compound_id = compound_id
        self.index = index
        self.body = body

    def encode(self):
        buffer = Buffer()
        buffer.write_byte(self.flags)
        buffer.write_unsigned_short(self.length_bits)

        if self.flags & 0x04:
            buffer.write_uint24le(self.reliable_index)

        if self.flags & 0x08:
            buffer.write_uint24le(self.sequenced_index)

        if self.flags & 0x10:
            buffer.write_uint24le(self.ordered_index)

        if self.flags & 0x20:
            buffer.write_byte(self.order_channel)

        if self.flags & 0x40:
            buffer.write_int(self.compound_size)

        if self.flags & 0x80:
            buffer.write_short(self.compound_id)

        if self.flags & 0x100:
            buffer.write_int(self.index)

        buffer.write(self.body)
        return buffer.getvalue()

    @staticmethod
    def decode(data):
        buffer = Buffer(data)
        flags = buffer.read_byte()
        length_bits = buffer.read_unsigned_short()

        reliable_index = buffer.read_uint24le() if flags & 0x04 else None
        sequenced_index = buffer.read_uint24le() if flags & 0x08 else None
        ordered_index = buffer.read_uint24le() if flags & 0x10 else None
        order_channel = buffer.read_byte() if flags & 0x20 else None
        compound_size = buffer.read_int() if flags & 0x40 else None
        compound_id = buffer.read_short() if flags & 0x80 else None
        index = buffer.read_int() if flags & 0x100 else None
        body = buffer.read((length_bits + 7) // 8)

        return Frame(flags, length_bits, reliable_index, sequenced_index, ordered_index, 
                     order_channel, compound_size, compound_id, index, body)

class FrameSetPacket:
    def __init__(self, packet_id, sequence_number, frames=None):
        self.packet_id = packet_id
        self.sequence_number = sequence_number
        self.frames = frames or []

    def encode(self):
        buffer = Buffer()
        buffer.write_byte(self.packet_id)
        buffer.write_uint24le(self.sequence_number)
        for frame in self.frames:
            buffer.write(frame.encode())
        return buffer.getvalue()

    @staticmethod
    def decode(data):
        buffer = Buffer(data)
        packet_id = buffer.read_byte()
        sequence_number = buffer.read_uint24le()

        frames = []
        while not buffer.feos():
            frame_start_pos = buffer.tell()
            
            frame = Frame.decode(buffer.getvalue()[frame_start_pos:])
            
            frames.append(frame)
            
            buffer.seek(frame_start_pos + (frame.length_bits + 7) // 8)
        
        return FrameSetPacket(packet_id, sequence_number, frames)