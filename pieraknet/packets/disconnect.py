from pieraknet.packets.packet import Packet


class Disconnect(Packet):
    packet_id = 0x15
    packet_type = 'disconnect'
