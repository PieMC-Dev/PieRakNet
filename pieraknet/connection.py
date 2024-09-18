from time import time
from pieraknet.packets.frame_set import Frame, FrameSetPacket
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
        self.client_sequence_number = 0
        self.server_sequence_number = 0
        self.queue = FrameSetPacket(server=self.server)
        self.last_receive_time = time()
        self.server.logger.info(f"Connection initialized: {self}")

    def update(self):
        if (time() - self.last_receive_time) >= self.server.timeout:
            self.server.logger.info(f"Connection timeout. Disconnecting {self.address}")
            self.disconnect()
        self.send_ack_queue()
        self.send_nack_queue()
        self.send_queue()

    def send_data(self, data: bytes):
        self.server.logger.debug(f"Sending data to {self.address}: {data}")
        self.server.send(data, self.address)

    def handle(self, data):
        self.last_receive_time = time()
        self.server.logger.info(f"Handling new packet from {self.address}: {data}")
        packet_type = data[0]
        handlers = {
            ProtocolInfo.ACK: self.handle_ack,
            ProtocolInfo.NACK: self.handle_nack
        }
        if ProtocolInfo.FRAME_SET_0 <= packet_type <= ProtocolInfo.FRAME_SET_F:
            self.handle_frame_set(data)
        elif packet_type in handlers:
            handlers[packet_type](data)
        elif packet_type == ProtocolInfo.DISCONNECT:
            self.handle_disconnect(data)
        else:
            self.server.logger.warning(f"Unhandled packet type {packet_type} from {self.address}")

    def handle_ack(self, data: bytes):
        self.server.logger.info(f"Handling ACK packet: {data}")
        packet = Ack(data)
        packet.decode()
        self.server.logger.debug(f"Decoded ACK packet: {packet}")
        for sequence_number in packet.sequence_numbers:
            self.recovery_queue.pop(sequence_number, None)

    def handle_nack(self, data: bytes):
        self.server.logger.info(f"Handling NACK packet: {data}")
        packet = Nack(data)
        packet.decode()
        self.server.logger.debug(f"Decoded NACK packet: {packet}")
        for sequence_number in packet.sequence_numbers:
            if sequence_number in self.recovery_queue:
                self.server.logger.info(f"Resending lost packet for sequence number {sequence_number}")
                lost_packet = self.recovery_queue[sequence_number]
                lost_packet.sequence_number = self.server_sequence_number
                self.server_sequence_number += 1
                self.send_data(lost_packet.encode())

    def handle_frame_set(self, data):
        self.server.logger.info(f"Handling Frame Set packet: {data}")
        frame_set_packet = FrameSetPacket(server=self.server)
        frame_set_packet.decode(Buffer(data))
        incoming_sequence_number = frame_set_packet.sequence_number
        self.server.logger.debug(f"Incoming sequence number: {incoming_sequence_number}")

        if incoming_sequence_number not in self.client_sequence_numbers:
            self.client_sequence_numbers.append(incoming_sequence_number)
            self.ack_queue.append(incoming_sequence_number)
            self.handle_packet_loss(incoming_sequence_number)
            self.client_sequence_number = incoming_sequence_number

            for frame in frame_set_packet.frames:
                if frame.flags & 0x01:
                    self.handle_fragmented_frame(frame)
                else:
                    self.handle_frame(frame)

    def handle_packet_loss(self, incoming_sequence_number):
        hole_size = incoming_sequence_number - self.client_sequence_number
        if hole_size > 0:
            self.server.logger.info(f"Detected packet loss. Hole size: {hole_size}")
            self.nack_queue.extend(range(self.client_sequence_number + 1, incoming_sequence_number))

    def handle_fragmented_frame(self, packet):
        self.server.logger.info(f"Handling Fragmented Frame: {packet}")
        fragments = self.fragmented_packets.setdefault(packet.compound_id, {})
        fragments[packet.index] = packet
        if len(fragments) == packet.compound_size:
            self.server.logger.info(f"Reassembling fragmented frame for compound_id {packet.compound_id}")
            body = b''.join(fragments[i].body for i in range(packet.compound_size))
            new_frame = Frame(flags=0, length_bits=0, body=body)
            del self.fragmented_packets[packet.compound_id]
            self.handle_frame(new_frame)

    def handle_frame(self, frame):
        self.server.logger.info(f"Handling Frame: {frame}")
        if not (hasattr(frame, 'flags') and hasattr(frame, 'body')):
            self.server.logger.error("Invalid packet structure")
            return

        if not self.connected:
            self.handle_connection_requests(frame)
        else:
            self.handle_established_connection(frame)

    def handle_connection_requests(self, frame):
        packet_type = frame.body[0]
        if packet_type == ProtocolInfo.CONNECTION_REQUEST:
            ConnectionRequestHandler.handle(frame.body, server=self.server, connection=self)
        elif packet_type == ProtocolInfo.NEW_INCOMING_CONNECTION:
            self.handle_new_incoming_connection(frame)
        else:
            self.server.logger.info(f"Unknown packet type: {packet_type}, aborting connection.")

    def handle_new_incoming_connection(self, frame):
        try:
            packet = NewIncomingConnection(frame.body)
            packet.decode()
            if packet.server_address[1] == self.server.port:
                self.connected = True
                self.server.logger.info(f"Connection established with {self.address}")
                if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_new_incoming"):
                    self.server.interface.on_new_incoming(self)
        except Exception as e:
            self.server.logger.error(f"Error decoding New Incoming Connection packet: {e}")

    def handle_established_connection(self, frame):
        packet_type = frame.body[0]
        if packet_type == ProtocolInfo.ONLINE_PING:
            self.process_online_ping(frame)
        elif packet_type == ProtocolInfo.GAME_PACKET:
            self.process_game_packet(frame)
        elif packet_type == ProtocolInfo.DISCONNECT:
            self.handle_disconnect(frame.body)
        else:
            self.process_unknown_packet(frame)

    def process_online_ping(self, frame):
        try:
            response_frame = Frame(flags=0, length_bits=0)
            response_frame.body = OnlinePingHandler.handle(OnlinePing(frame.body), self, self.server)
            self.add_to_queue(response_frame, is_immediate=False)
        except Exception as e:
            self.server.logger.error(f"Error handling ONLINE_PING: {e}")

    def process_game_packet(self, frame):
        if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_game_packet"):
            self.server.interface.on_game_packet(frame.body, self)

    def process_unknown_packet(self, frame):
        if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_unknown_packet"):
            self.server.interface.on_unknown_packet(frame.body, self)

    def handle_disconnect(self, data):
        self.server.logger.info(f"Handling DISCONNECT packet: {data}")
        self.disconnect()

    def add_to_queue(self, packet: Frame, is_immediate=True):
        if not isinstance(packet, Frame):
            self.server.logger.error(f"Error: Expected Frame, got {type(packet)}")
            return

        self.server.logger.info(f"Adding packet to queue: {packet}, immediate: {is_immediate}")
        encoded_packet = packet.encode(buffer=Buffer())

        if len(encoded_packet) > self.mtu_size:
            self.fragment_and_queue(encoded_packet, packet)
        else:
            self.queue.add_frame(packet)

        if is_immediate:
            self.send_queue()

    def fragment_and_queue(self, encoded_packet, packet):
        self.server.logger.info(f"Fragmenting packet as it exceeds MTU size: {self.mtu_size}")
        fragmented_body = [encoded_packet[i:i + self.mtu_size] for i in range(0, len(encoded_packet), self.mtu_size)]
        for index, body in enumerate(fragmented_body):
            fragment = Frame(
                flags=packet.flags | 0x01,
                length_bits=len(body) * 8,
                compound_id=self.compound_id,
                index=index,
                body=body
            )
            self.add_to_queue(fragment, is_immediate=False)
        self.compound_id += 1

    def send_ack_queue(self):
        while self.ack_queue:
            sequence_number = self.ack_queue.pop(0)
            ack_packet = Ack(sequence_number)
            self.send_data(ack_packet.encode())

    def send_nack_queue(self):
        while self.nack_queue:
            sequence_number = self.nack_queue.pop(0)
            nack_packet = Nack([sequence_number])
            self.send_data(nack_packet.encode())

    def disconnect(self):
        self.server.logger.info(f"Disconnecting connection: {self.address}")
        disconnect_packet = Disconnect()
        self.send_data(disconnect_packet.encode())
        self.connected = False
        self.server.remove_connection(self)

    def __repr__(self):
        return f"Connection(address={self.address}, guid={self.guid})"
