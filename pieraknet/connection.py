import time
import collections
from pieraknet.buffer import Buffer
from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.connection_request import ConnectionRequestHandler
from pieraknet.handlers.new_incoming_connection import NewIncomingConnectionHandler
from pieraknet.handlers.acknowledgement import AckHandler, NackHandler
from pieraknet.handlers.frame_set import FrameSetHandler
from pieraknet.handlers.disconnect import DisconnectHandler
from pieraknet.handlers.packet_loss import PacketLossHandler
from pieraknet.handlers.online_ping import OnlinePingHandler

class Connection:
    def __init__(self, server, address):
        self.server = server
        self.address = address
        self.connected = False
        self.client_sequence_number = 0
        self.server_sequence_number = 0
        self.ack_queue = collections.deque()  # Optimized for append/pop operations
        self.nack_queue = collections.deque()
        self.recovery_queue = collections.OrderedDict()  # Keep recovery packets in order
        self.client_sequence_numbers = set()  # Efficient lookups for incoming sequence numbers
        self.fragmented_packets = {}
        self.logger = server.logger
        self.logger.debug(f"Created connection: {self} for address {self.address}")

    def disconnect(self):
        self.server.logger.debug(f"Disconnecting {self.address}")
        self.connected = False
        self.ack_queue.clear()
        self.nack_queue.clear()
        self.recovery_queue.clear()
        self.server.remove_connection(self)

    def handle(self, data):
        """ Handle incoming packets based on packet_id """
        packet_id = data[0]

        handler_map = {
            ProtocolInfo.ACK: AckHandler.handle,
            ProtocolInfo.NACK: NackHandler.handle,
            ProtocolInfo.DISCONNECT: DisconnectHandler.handle,
            **{pid: FrameSetHandler.handle for pid in range(ProtocolInfo.FRAME_SET_0, ProtocolInfo.FRAME_SET_F + 1)},
        }

        if handler := handler_map.get(packet_id):
            handler(data, self.server, self)
        else:
            self.server.logger.error(f"Unknown packet ID: {packet_id}")

    def process_retransmissions(self):
        """ Retry sending unacknowledged packets """
        current_time = time.time()
        to_resend = []

        for seq_num, (packet, timestamp) in list(self.recovery_queue.items()):
            if current_time - timestamp > self.server.timeout:
                to_resend.append((seq_num, packet))
                self.logger.debug(f"Resending packet with sequence number {seq_num}")

        for seq_num, packet in to_resend:
            self.send_data(packet)

    def update(self):
        """ Periodically check for lost packets and handle ACK/NACK """
        self.acknowledge()
        self.process_retransmissions()

    def handle_packet_loss(self, incoming_sequence_number):
        """ Detect and handle lost packets """
        missing_packets = range(self.client_sequence_number + 1, incoming_sequence_number)
        if missing_packets:
            self.nack_queue.extend(missing_packets)
            PacketLossHandler.handle(incoming_sequence_number, self.server, self)

    def handle_connection_requests(self, frame):
        packet_type = frame['body'][0]
        if packet_type == ProtocolInfo.CONNECTION_REQUEST:
            OnlinePingHandler.create_online_ping(self.server, self)
            connection_packet = ConnectionRequestHandler.handle(frame['body'], self.server, self)
            # Crear un FrameSetPacket
            frame_set_packet = FrameSetPacket(self.server)
            frame_set_packet.sequence_number = self.client_sequence_number
            frame_set_packet.create_frame(connection_packet, flags=0x64)

            # Codificar y enviar directamente sin usar Buffer
            self.send_data(frame_set_packet.encode())
            self.connected = True
        elif packet_type == ProtocolInfo.NEW_INCOMING_CONNECTION:
            NewIncomingConnectionHandler.handle(frame['body'], self.server, self)

    def send_data(self, data):
        self.server.send(data, self.address)
        # if its a frame set packet
        if ProtocolInfo.FRAME_SET_0 <= data[0] <= ProtocolInfo.FRAME_SET_F:
            self.recovery_queue[self.server_sequence_number] = (data, time.time())
            self.server_sequence_number += 1

    def acknowledge(self):
        """ Send accumulated ACKs """
        if self.ack_queue:
            ack_packet = AckHandler.create_ack_packet(list(self.ack_queue))
            self.send_data(ack_packet)
            self.ack_queue.clear()

        if self.nack_queue:
            nack_packet = NackHandler.create_nack_packet(list(self.nack_queue))
            self.send_data(nack_packet)
            self.nack_queue.clear()
