import time
from pieraknet.packets.frame_set import FrameSet, Frame
from pieraknet.protocol_info import ProtocolInfo
from pieraknet.packets.acknowledgement import Ack, Nack
from pieraknet.handlers.connection_request import ConnectionRequestHandler
from pieraknet.handlers.online_ping import OnlinePingHandler
from pieraknet.packets.online_ping import OnlinePing
from pieraknet.packets.new_incoming_connection import NewIncomingConnection
from pieraknet.packets.disconnect import Disconnect
from pieraknet.buffer import Buffer

class Connection:
    def __init__(self, address, server, mtu_size, guid):
        self.address = address
        self.mtu_size = mtu_size
        self.server = server
        self.guid = guid
        self.connected = False
        self.recovery_queue = {}
        self.ack_queue = []
        self.nack_queue = []
        self.fragmented_packets = {}
        self.compound_id = 0
        self.client_sequence_numbers = []
        # self.server_sequence_numbers = []
        self.client_sequence_number = 0
        self.server_sequence_number = 0
        self.queue = FrameSet()
        self.server_reliable_frame_index = 0
        self.client_reliable_frame_index = 0
        self.channel_index = [0] * 32
        self.last_receive_time = time.time()

    def update(self):
        if (time.time() - self.last_receive_time) >= self.server.timeout:
            self.disconnect()
        self.send_ack_queue()
        self.send_nack_queue()
        self.send_queue()

    def send_data(self, data: bytes):
        self.server.send(data, self.address)

    def handle(self, data):
        self.last_receive_time = time.time()
        print("New Packet: ", data)  # Log the received packet data
        if data[0] == ProtocolInfo.ACK:
            self.handle_ack(data)
        elif data[0] == ProtocolInfo.NACK:
            self.handle_nack(data)
        elif ProtocolInfo.FRAME_SET_0 <= data[0] <= ProtocolInfo.FRAME_SET_F:
            self.handle_frame_set(data)  # Pass the raw binary data to the method
            print("Frame Set handled.")  # Log that the frame set was handled


    def handle_ack(self, data: bytes):
        print("Handling ACK packet...")
        packet = Ack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                del self.recovery_queue[sequence_number]

    def handle_nack(self, data: bytes):
        print("Handling NACK packet...")
        packet = Nack(data)
        packet.decode()
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                lost_packet = self.recovery_queue[sequence_number]
                lost_packet.sequence_number = self.server_sequence_number
                self.server_sequence_number += 1
                lost_packet.encode()
                self.send_data(lost_packet.data)
                del self.recovery_queue[sequence_number]

    def handle_frame_set(self, data):
        print("Handling Frame Set...")
        buf = Buffer(data)  # Create a Buffer instance from the received data
        frame_set = FrameSet()
        frame_set.decode(data)  # Pass the Buffer instance to the decode method
        if frame_set.sequence_number not in self.client_sequence_numbers:
            if frame_set.sequence_number in self.nack_queue:
                self.nack_queue.remove(frame_set.sequence_number)
            self.client_sequence_numbers.append(frame_set.sequence_number)
            self.ack_queue.append(frame_set.sequence_number)
            hole_size = frame_set.sequence_number - self.client_sequence_number
            if hole_size > 0:
                for sequence_number in range(self.client_sequence_number + 1, hole_size):
                    if sequence_number not in self.client_sequence_numbers:
                        self.nack_queue.append(sequence_number)
            self.client_sequence_number = frame_set.sequence_number
            for frame in frame_set.frames:
                if not (2 <= frame.reliability <= 7 and frame.reliability != 5):
                    self.handle_frame(frame)
                else:
                    hole_size = frame.reliable_frame_index - self.client_reliable_frame_index
                    if hole_size == 0:
                        self.handle_frame(frame)
                        self.client_reliable_frame_index += 1


    def handle_fragmented_frame(self, packet):
        print("Handling Fragmented Frame...")
        if packet.compound_id not in self.fragmented_packets:
            self.fragmented_packets[packet.compound_id] = {packet.index: packet}
        else:
            self.fragmented_packets[packet.compound_id][packet.index] = packet
        if len(self.fragmented_packets[packet.compound_id]) == packet.compound_size:
            new_frame = Frame()
            new_frame.body = b''
            for i in range(0, packet.compound_size):
                new_frame.body += self.fragmented_packets[packet.compound_id][i].body
            del self.fragmented_packets[packet.compound_id]
            self.handle_frame(new_frame)

    def handle_frame(self, packet):
        print("Handling Frame...")
        if packet.fragmented:
            self.handle_fragmented_frame(packet)
        else:
            if not self.connected:
                if packet.body[0] == ProtocolInfo.CONNECTION_REQUEST:
                    new_frame = Frame()
                    new_frame.reliability = 0
                    new_frame.body = ConnectionRequestHandler.handle(packet.body, self.server, self)
                    self.add_to_queue(new_frame)
                elif packet.body[0] == ProtocolInfo.NEW_INCOMING_CONNECTION:
                    packet = NewIncomingConnection(packet.body)
                    packet.decode()
                    if packet.server_address[1] == self.server.port:
                        self.connected = True
                        if hasattr(self.server, "interface"):
                            if hasattr(self.server.interface, "on_new_incoming_connection"):
                                self.server.interface.on_new_incoming_connection(self)
            elif packet.body[0] == ProtocolInfo.ONLINE_PING:
                new_frame = Frame()
                new_frame.reliability = 0
                new_frame.body = OnlinePingHandler.handle(OnlinePing(packet.body), self, self.server)
                self.add_to_queue(new_frame, False)
            elif packet.body[0] == ProtocolInfo.DISCONNECT:
                self.disconnect()
            elif packet.body[0] == ProtocolInfo.GAME_PACKET:
                if hasattr(self.server, "interface"):
                    if hasattr(self.server.interface, "on_game_packet"):
                        self.server.interface.on_game_packet(packet, self)
            else:
                if hasattr(self.server, "interface"):
                    if hasattr(self.server.interface, "on_unknown_packet"):
                        self.server.interface.on_unknown_packet(packet, self)

    def send_queue(self):
        print("Sending Queue...")
        if len(self.queue.frames) > 0:
            self.queue.sequence_number = self.server_sequence_number
            self.server_sequence_number += 1
            self.recovery_queue[self.queue.sequence_number] = self.queue
            self.queue.encode()
            self.send_data(self.queue.getvalue())
            self.queue = FrameSet()

    def add_to_queue(self, packet: Frame, is_immediate=True):
        if 2 <= packet.reliability <= 7 and packet.reliability != 5:
            packet.reliable_frame_index = self.server_reliable_frame_index
            self.server_reliable_frame_index += 1
            if packet.reliability == 3:
                packet.ordered_frame_index = self.channel_index[packet.order_channel]
                self.channel_index[packet.order_channel] += 1
        if packet.get_size() > self.mtu_size:
            fragmented_body = []
            for i in range(0, len(packet.body), self.mtu_size):
                fragmented_body.append(packet.body[i:i + self.mtu_size])
            for index, body in enumerate(fragmented_body):
                new_packet = Frame()
                new_packet.fragmented = True
                new_packet.reliability = packet.reliability
                new_packet.compound_id = self.compound_id
                new_packet.compound_size = len(fragmented_body)
                new_packet.index = index
                new_packet.body = body
                if index != 0:
                    new_packet.reliable_frame_index = self.server_reliable_frame_index
                    self.server_reliable_frame_index += 1
                if new_packet.reliability == 3:
                    new_packet.ordered_frame_index = packet.ordered_frame_index
                    new_packet.order_channel = packet.order_channel
                if is_immediate:
                    self.queue.frames.append(new_packet)
                    self.send_queue()
                else:
                    frame_size: int = new_packet.get_size()
                    queue_size: int = self.queue.get_size()
                    if frame_size + queue_size >= self.mtu_size:
                        self.send_queue()
                    self.queue.frames.append(new_packet)
            self.compound_id += 1
        else:
            if is_immediate:
                self.queue.frames.append(packet)
                self.send_queue()
            else:
                frame_size: int = packet.get_size()
                queue_size: int = self.queue.get_size()
                if frame_size + queue_size >= self.mtu_size:
                    self.send_queue()
                self.queue.frames.append(packet)

    def send_ack_queue(self):
        if len(self.ack_queue) > 0:
            packet = Ack()
            packet.sequence_numbers = self.ack_queue
            self.ack_queue = []
            packet.encode()
            self.send_data(packet.getvalue())

    def send_nack_queue(self):
        if len(self.nack_queue) > 0:
            packet = Nack()
            packet.sequence_numbers = self.nack_queue
            self.nack_queue = []
            packet.encode()
            self.send_data(packet.getvalue())

    def disconnect(self):
        print("Disconnecting...")
        new_frame = Frame()
        new_frame.reliability = 0
        disconnect_packet = Disconnect()
        disconnect_packet.encode()
        new_frame.body = disconnect_packet.getvalue()
        self.add_to_queue(new_frame)
        self.server.remove_connection(self.address)
        if hasattr(self.server, "interface"):
            if hasattr(self.server.interface, "on_disconnect"):
                self.server.interface.on_disconnect(self)