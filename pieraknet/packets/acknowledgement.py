from pieraknet.packets.packet import Packet
from pieraknet.buffer import Buffer
from pieraknet.protocol_info import ProtocolInfo

class Acknowledgement(Packet):
    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.sequence_numbers: list[int] = []

    def decode_payload(self):
        """ Decode the payload to extract sequence numbers. """
        self.sequence_numbers.clear()
        count: int = self.read_short()
        for _ in range(count):
            single: bool = self.read_bool()
            if single:
                self.sequence_numbers.append(self.read_uint24le())
            else:
                start_index: int = self.read_uint24le()
                end_index: int = self.read_uint24le()
                self.sequence_numbers.extend(range(start_index, end_index + 1))

    def encode_payload(self):
        """ Encode the sequence numbers into the payload. """
        self.sequence_numbers.sort()
        temp_buffer: Buffer = Buffer()
        count: int = 0

        # Iterate through sequence numbers and create ranges
        start_index: int = self.sequence_numbers[0]
        end_index: int = start_index
        for index in self.sequence_numbers[1:]:
            if index == end_index + 1:
                end_index = index
            else:
                self._write_range(temp_buffer, start_index, end_index)
                count += 1
                start_index = end_index = index
        
        # Write the last range
        self._write_range(temp_buffer, start_index, end_index)
        count += 1
        
        self.write_short(count)
        self.write(temp_buffer.getvalue())

    def _write_range(self, buffer: Buffer, start: int, end: int):
        """ Helper method to write a range of sequence numbers. """
        if start == end:
            buffer.write_bool(True)
            buffer.write_uint24le(start)
        else:
            buffer.write_bool(False)
            buffer.write_uint24le(start)
            buffer.write_uint24le(end)

class Nack(Acknowledgement):
    PACKET_ID = ProtocolInfo.NACK

class Ack(Acknowledgement):
    PACKET_ID = ProtocolInfo.ACK
