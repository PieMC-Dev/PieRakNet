from pieraknet.buffer import Buffer
from pieraknet.packets.packet import Packet
from pieraknet.packets.frame import Frame

# Example packet: b'\x84\x00\x00\x00\x40\x00\x90\x00\x00\x00\t\xb3;\xc81\xbe\xfb\x96*\x00\x00\x00\x00\x00\x00\xdb\xf2\x00'
# x84: Packet ID
# Sequence number: uint24le (en este caso \x00\x00\x00)
# Flags (byte): (en este caso \x40)
#   reliability_type = top 3 bits
#   fourth bit is 1 when the frame is fragmented and part of a compound.
# Length IN BITS (unsigned short): Length of the body in bits. (en este caso \x00\x90)
# Reliable Frame Index (uint24le): only if reliable (en este caso \x00\x00\x00)
# Sequenced Frame Index (uint24le): only if sequenced (en este caso \x00\x00\x00)
# --- ORDER --- 
# Ordered Frame Index (uint24le): only if ordered (en este caso \x00)
# Order Channel (byte): only if ordered (en este caso \x00)
# --- FRAGMENT ---
# Compound Size (int): only if fragmented (en este caso \x00\x00\x00)
# Compound ID (short): only if fragmented (en este caso \x00\x00)
# Index (int): only if fragmented (en este caso \x00\x00\x00\x00)
# --- BODY ---
# Body (length in bits / 8): only if not fragmented (en este caso \xdb\xf2\x00)



#ID	Name                    Reliable    Ordered    Sequenced
#0	unreliable			    
#1	unreliable sequenced		          x	           x
#2	reliable	              x		
#3	reliable ordered 	      x           x	
#4	reliable sequenced	      x           x	           x
#5	unreliable (+ ACK receipt)			
#6	reliable (+ ACK receipt)  x		
#7	reliable ordered (+ ACK receipt)x	  x	


class FrameSetPacket:
    def __init__(self, server=None):
        self.server = server
        self.packet_id = 0
        self.sequence_number = 0
        self.frames = []

    def decode(self, buffer: Buffer):
        self.packet_id = buffer.read_byte()
        self.server.logger.debug(f"Read Packet ID: {self.packet_id}")

        self.sequence_number = buffer.read_uint24le()
        self.server.logger.debug(f"Read Sequence Number: {self.sequence_number}")

        while not buffer.feos():
            frame = Frame(self.server)
            frame.decode(buffer)
            self.frames.append(frame)
            self.server.logger.debug(f"Read Frame: {frame}")

    def encode(self, buffer: Buffer):
        buffer.write_byte(self.packet_id)
        self.server.logger.debug(f"Written Packet ID: {self.packet_id}")
        
        buffer.write_uint24le(self.sequence_number)
        self.server.logger.debug(f"Written Sequence Number: {self.sequence_number}")
        
        for frame in self.frames:
            buffer.write(frame.encode(buffer = Buffer()))
            self.server.logger.debug(f"Written Frame: {frame}")
        
        return buffer.getvalue()
    
    def add_frame(self, frame):
        if not isinstance(frame, Frame):
            raise TypeError("Expected a Frame instance.")
        self.frames.append(frame)