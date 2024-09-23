import time
from pieraknet.buffer import Buffer
from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.packets.online_ping import OnlinePing
from pieraknet.protocol_info import ProtocolInfo
from pieraknet.handlers.connection_request import ConnectionRequestHandler
from pieraknet.handlers.new_incoming_connection import NewIncomingConnectionHandler
from pieraknet.handlers.established_connection import EstablishedConnectionHandler
from pieraknet.handlers.online_ping import OnlinePingHandler
from pieraknet.handlers.game_packet import GamePacketHandler
from pieraknet.handlers.unknown_packet import UnknownPacketHandler
from pieraknet.handlers.ack import AckHandler
from pieraknet.handlers.nack import NackHandler
from pieraknet.handlers.frame_set import FrameSetHandler
from pieraknet.handlers.disconnect import DisconnectHandler
from pieraknet.handlers.packet_loss import PacketLossHandler

class Connection:
    def __init__(self, server, address):
        self.server = server
        self.address = address
        self.connected = False
        self.client_sequence_number = 0
        self.server_sequence_number = 0
        self.ack_queue = []
        self.nack_queue = []
        self.recovery_queue = {}
        self.client_sequence_numbers = []
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
        # Determine the packet type and delegate to the appropriate handler
        packet_id = data[0]

        if packet_id == ProtocolInfo.ACK:
            AckHandler.handle(data, self.server, self)
        elif packet_id == ProtocolInfo.NACK:
            NackHandler.handle(data, self.server, self)
        elif ProtocolInfo.FRAME_SET_0 <= packet_id <= ProtocolInfo.FRAME_SET_F:
            FrameSetHandler.handle(data, self.server, self)
        elif packet_id == ProtocolInfo.DISCONNECT:
            DisconnectHandler.handle(data, self.server, self)
        else:
            self.server.logger.error(f"Unknown packet ID: {packet_id}")

    def handle_packet_loss(self, incoming_sequence_number):
        if incoming_sequence_number in self.recovery_queue:
            self.logger.warning(f"Packet loss detected for sequence number {incoming_sequence_number}. Retransmitting...")
            lost_packet = self.recovery_queue[incoming_sequence_number]
            self.send_data(lost_packet)
        PacketLossHandler.handle(incoming_sequence_number, self.server, self)

    # Handle connection request (if frame is 0x09)
    def handle_connection_requests(self, frame):
        packet_type = frame.body[0]
        if packet_type == ProtocolInfo.CONNECTION_REQUEST:
            self._process_connection_request(frame)
        elif packet_type == ProtocolInfo.NEW_INCOMING_CONNECTION:
            NewIncomingConnectionHandler.handle(frame.body, self.server, self)

    
    def _process_connection_request(self, frame):
        connection_packet = ConnectionRequestHandler.handle(frame.body, self.server, self)
        frame_set_packet = FrameSetPacket().create_frame_set_packet(connection_packet, flags=0x64)
        buffer = Buffer()
        frame_set_packet.encode(connection=self, buffer=buffer)
        self.send_data(buffer.getvalue())

    def handle_established_connection(self, frame):      
        EstablishedConnectionHandler.handle(frame, self.server, self)

    def process_online_ping(self, frame):
        self.server.logger.debug(f"Received Online Ping from {self.address}")

        OnlinePongPacket = OnlinePingHandler.handle(OnlinePing(frame.body), self.server, self)

        frameSetPacket = FrameSetPacket().create_frame_set_packet(OnlinePongPacket, flags=0x00)

        buffer = Buffer()
        frameSetPacket.encode(connection=self, buffer=buffer)

        self.send_data(buffer.getvalue())
        self.server.logger.info(f"We have just sent an Online Pong to {self.address}")

    def process_game_packet(self, frame):
        GamePacketHandler.handle(frame.body, self.server, self)

    def handle_disconnect(self, frame_body):
        DisconnectHandler.handle(frame_body, self.server, self)

    def process_unknown_packet(self, frame):
        UnknownPacketHandler.handle(frame.body, self.server, self)

    def send_data(self, data):
        self.server.send(data, self.address)
        self.recovery_queue[self.server_sequence_number] = (data, time.time())  # Track sent data with timestamp
        self.server_sequence_number += 1

    def acknowledge(self):
        # Send ACK packets for the processed sequence numbers
        if self.ack_queue:
            ack_packet = AckHandler.create_ack_packet(self.ack_queue)
            self.send_data(ack_packet)
            self.ack_queue.clear()

    def negative_acknowledge(self):
        # Send NACK packets for the lost sequence numbers
        if self.nack_queue:
            nack_packet = NackHandler.create_nack_packet(self.nack_queue)
            self.send_data(nack_packet)
            self.nack_queue.clear()

    def update(self):
        self.acknowledge()
        self.negative_acknowledge()
        
        # Check for packet timeouts
        current_time = time.time()
        to_resend = []
        for seq_num, (packet, timestamp) in self.recovery_queue.items():
            if current_time - timestamp > self.server.timeout:
                to_resend.append((seq_num, packet))
                self.logger.debug(f"Resending packet with sequence number {seq_num}")
        
        for seq_num, packet in to_resend:
            self.send_data(packet)
            self.recovery_queue[seq_num] = (packet, current_time)  # Reset the timestamp
