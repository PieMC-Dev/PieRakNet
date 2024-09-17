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
        self.incoming_sequence_number = 0
        self.queue = FrameSetPacket()
        self.server_reliable_frame_index = 0
        self.client_reliable_frame_index = 0
        self.channel_index = [0] * 32
        self.last_receive_time = time()
        self.server.logger.info(f"Connection initialized: {self}")

    def update(self):
        self.server.logger.debug(f"Updating connection: {self}")
        if (time() - self.last_receive_time) >= self.server.timeout:
            self.server.logger.info(f"Connection timeout. Last receive time: {self.last_receive_time}, Current time: {time()}")
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
        if packet_type == ProtocolInfo.ACK:
            self.handle_ack(data)
        elif packet_type == ProtocolInfo.NACK:
            self.handle_nack(data)
        elif ProtocolInfo.FRAME_SET_0 <= packet_type <= ProtocolInfo.FRAME_SET_F:
            self.handle_frame_set(data)
        else:
            self.server.logger.warning(f"Unhandled packet type {packet_type} from {self.address}")

    def handle_ack(self, data: bytes):
        self.server.logger.info(f"Handling ACK packet: {data}")
        packet = Ack(data)
        packet.decode()
        self.server.logger.debug(f"Decoded ACK packet: {packet}")
        for sequence_number in packet.sequence_numbers:
            self.server.logger.debug(f"Removing sequence number {sequence_number} from recovery queue")
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
                lost_packet.encode()
                self.send_data(lost_packet.data)
                del self.recovery_queue[sequence_number]

    def handle_frame_set(self, data):
        self.server.logger.info(f"Handling Frame Set packet: {data}")

        # Create a FrameSetPacket
        frame_set_packet = FrameSetPacket(server=self.server)
        frame_set_packet.decode(Buffer(data))

        # Verificar números de secuencia
        incoming_sequence_number = frame_set_packet.sequence_number
        self.server.logger.debug(f"Incoming sequence number: {incoming_sequence_number}")

        if incoming_sequence_number not in self.client_sequence_numbers:
            self.client_sequence_numbers.append(incoming_sequence_number)
            self.ack_queue.append(incoming_sequence_number)
            self.server.logger.debug(f"Updated ACK queue: {self.ack_queue}")

            hole_size = incoming_sequence_number - self.client_sequence_number
            if hole_size > 0:
                self.server.logger.info(f"Detected packet loss. Hole size: {hole_size}")
                self.nack_queue.extend(range(self.client_sequence_number + 1, incoming_sequence_number))

            self.client_sequence_number = incoming_sequence_number

            for frame in frame_set_packet.frames:
                if not (2 <= frame.flags <= 7 and frame.flags != 5):
                    self.server.logger.debug(f"Handling frame")
                    self.handle_frame(frame)
                else:
                    self.server.logger.debug(f"Handling frame: {frame.flags}")
                    hole_size = frame.reliable_frame_index - self.client_reliable_frame_index
                    if hole_size == 0:
                        self.handle_frame(frame)
                        self.client_reliable_frame_index += 1
                    elif hole_size > 0:
                        self.nack_queue.append(self.client_reliable_frame_index + 1)
                        self.client_reliable_frame_index = frame.reliable_frame_index
                        self.handle_frame(frame)

    def handle_fragmented_frame(self, packet):
        self.server.logger.info(f"Handling Fragmented Frame: {packet}")
        fragments = self.fragmented_packets.setdefault(packet.compound_id, {})
        fragments[packet.index] = packet
        self.server.logger.debug(f"Updated fragments for compound_id {packet.compound_id}: {fragments}")
        if len(fragments) == packet.compound_size:
            self.server.logger.info(f"Reassembling fragmented frame for compound_id {packet.compound_id}")
            new_frame = Frame(flags=0, length_bits=0)
            new_frame.body = b''.join(fragments[i].body for i in range(packet.compound_size))
            del self.fragmented_packets[packet.compound_id]
            self.handle_frame(new_frame)

    def handle_frame(self, packet):
        self.server.logger.info(f"Handling Frame: {packet}")

        # Verifica que el paquete tenga el atributo 'flags' y 'body'
        if not hasattr(packet, 'flags') or not hasattr(packet, 'body'):
            self.server.logger.error("Invalid packet structure")
            return

        # Maneja los paquetes fragmentados
        if packet.flags & 0x01:
            self.server.logger.debug(f"Handling fragmented frame")
            self.handle_fragmented_frame(packet)
        else:
            self.server.logger.debug(f"Handling non-fragmented frame")
            # Determina el tipo de paquete
            packet_type = packet.body[0]
            self.server.logger.debug(f"Packet type: {packet_type}")

            if not self.connected:
                self.server.logger.info(f"Connection not established, handling packet type: {packet_type}")
                if packet_type == ProtocolInfo.CONNECTION_REQUEST:
                    new_frame = Frame(flags=0, length_bits=0)
                    try:
                        new_frame.body = ConnectionRequestHandler.handle(packet.body, self.server, self)
                    except Exception as e:
                        self.server.logger.error(f"Error handling CONNECTION_REQUEST: {e}")
                        return
                    self.add_to_queue(new_frame)
                elif packet_type == ProtocolInfo.NEW_INCOMING_CONNECTION:
                    packet = NewIncomingConnection(packet.body)
                    try:
                        packet.decode()
                    except Exception as e:
                        self.server.logger.error(f"Error decoding New Incoming Connection packet: {e}")
                        return
                    self.server.logger.debug(f"Decoded New Incoming Connection packet: {packet}")
                    if packet.server_address[1] == self.server.port:
                        self.connected = True
                        self.server.logger.info(f"Connection established with {self.address}")
                        if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_new_incoming"):
                            self.server.interface.on_new_incoming(self)
                else:
                    self.server.logger.info(f"Uknown packet type: {packet_type}, aborting connection.")

            else:
                self.server.logger.info(f"Connection established, handling packet type: {packet_type}")
                if packet_type == ProtocolInfo.ONLINE_PING:
                    new_frame = Frame(flags=0, length_bits=0)
                    try:
                        new_frame.body = OnlinePingHandler.handle(OnlinePing(packet.body), self, self.server)
                    except Exception as e:
                        self.server.logger.error(f"Error handling ONLINE_PING: {e}")
                        return
                    self.add_to_queue(new_frame, False)
                elif packet_type == ProtocolInfo.DISCONNECT:
                    self.disconnect()
                elif packet_type == ProtocolInfo.GAME_PACKET:
                    if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_game_packet"):
                        self.server.interface.on_game_packet(packet, self)
                else:
                    if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_unknown_packet"):
                        self.server.interface.on_unknown_packet(packet, self)

    def send_queue(self):
        self.server.logger.debug(f"Sending packet queue for connection: {self.address}")
        if not self.queue.frames:
            self.server.logger.debug("No frames to send.")
            return

        self.queue.sequence_number = self.server_sequence_number
        self.server_sequence_number += 1
        self.recovery_queue[self.queue.sequence_number] = self.queue
        encoded_data = self.queue.encode()
        self.send_data(encoded_data)
        self.queue = FrameSetPacket()

    def add_to_queue(self, packet: Frame, is_immediate=True):
        self.server.logger.info(f"Adding packet to queue: {packet}, immediate: {is_immediate}")
        if 2 <= packet.flags <= 7 and packet.flags != 5:
            packet.reliable_index = self.server_reliable_frame_index
            self.server_reliable_frame_index += 1
            if packet.flags & 0x10:
                packet.ordered_index = self.channel_index[packet.order_channel]
                self.channel_index[packet.order_channel] += 1

        if len(packet.encode()) > self.mtu_size:
            self.server.logger.info(f"Fragmenting packet as it exceeds MTU size: {self.mtu_size}")
            fragmented_body = [packet.body[i:i + self.mtu_size] for i in range(0, len(packet.body), self.mtu_size)]
            for index, body in enumerate(fragmented_body):
                new_packet = Frame(
                    flags=packet.flags | 0x01,
                    length_bits=len(body) * 8,
                    compound_id=self.compound_id,
                    compound_size=len(fragmented_body),
                    index=index,
                    body=body
                )
                self.queue.add_frame(new_packet)
            self.compound_id += 1
        else:
            self.queue.add_frame(packet)

        if is_immediate:
            self.send_queue()

    def send_ack_queue(self):
        if self.ack_queue:
            self.server.logger.debug(f"Sending ACK queue: {self.ack_queue}")
            packet = Ack()
            packet.sequence_numbers = self.ack_queue.copy()
            packet.encode()
            self.send_data(packet.data)
            self.ack_queue.clear()

    def send_nack_queue(self):
        if self.nack_queue:
            self.server.logger.debug(f"Sending NACK queue: {self.nack_queue}")
            packet = Nack()
            packet.sequence_numbers = self.nack_queue.copy()
            packet.encode()
            self.send_data(packet.data)
            self.nack_queue.clear()

    def disconnect(self):
        self.server.logger.info(f"Disconnecting from {self.address}")
        packet = Disconnect()
        packet.encode()
        self.send_data(packet.data)
        if hasattr(self.server, "interface") and hasattr(self.server.interface, "on_disconnect"):
            self.server.interface.on_disconnect(self)
