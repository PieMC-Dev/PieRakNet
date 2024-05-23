from pieraknet.packets.packet import Packet

class Disconnect(Packet):
    PACKET_ID = 0x15
    PACKET_TYPE = 'disconnect'

    def __init__(self, data: bytes = b''):
        super().__init__(data)
