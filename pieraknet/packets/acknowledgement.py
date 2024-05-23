from pieraknet.packets.packet import Packet
from pieraknet.buffer import Buffer
from pieraknet.protocol_info import ProtocolInfo

class Acknowledgement(Packet):
    def __init__(self, data: bytes = b''):
        super().__init__(data)
        self.sequence_numbers: list[int] = []

    def decode_payload(self) -> None:
        self.sequence_numbers.clear()
        count: int = self.read_short()
        for _ in range(count):
            single: bool = self.read_bool()
            if single:
                self.sequence_numbers.append(self.read_uint24le())
            else:
                start_index: int = self.read_uint24le()
                end_index: int = self.read_uint24le()
                for index in range(start_index, end_index + 1):
                    self.sequence_numbers.append(index)

    def encode_payload(self) -> None:
        self.sequence_numbers.sort()
        temp_buffer: Buffer = Buffer()
        count: int = 0
        start_index: int = self.sequence_numbers[0]
        end_index: int = start_index
        for index in self.sequence_numbers[1:]:
            if index == end_index + 1:
                end_index = index
            else:
                if start_index == end_index:
                    temp_buffer.write_bool(True)
                    temp_buffer.write_uint24le(start_index)
                else:
                    temp_buffer.write_bool(False)
                    temp_buffer.write_uint24le(start_index)
                    temp_buffer.write_uint24le(end_index)
                count += 1
                start_index = end_index = index
        if start_index == end_index:
            temp_buffer.write_bool(True)
            temp_buffer.write_uint24le(start_index)
        else:
            temp_buffer.write_bool(False)
            temp_buffer.write_uint24le(start_index)
            temp_buffer.write_uint24le(end_index)
        count += 1
        self.write_short(count)
        self.write(temp_buffer.getvalue())


class Nack(Acknowledgement):
    PACKET_ID = ProtocolInfo.NACK


class Ack(Acknowledgement):
    PACKET_ID = ProtocolInfo.ACK
