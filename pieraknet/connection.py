import time
from pieraknet.packets.frame_set import FrameSetPacket
from pieraknet.packets.online_ping import OnlinePing
from pieraknet.packets.connection_request import ConnectionRequest
from pieraknet.packets.connection_request_accepted import ConnectionRequestAccepted
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
from pieraknet.handlers.fragmented_frame import FragmentedFrameHandler
from pieraknet.handlers.frame import FrameHandler

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
        PacketLossHandler.handle(incoming_sequence_number, self.server, self)

    def handle_fragmented_frame(self, frame):
        FragmentedFrameHandler.handle(frame, self.server, self)

    def handle_frame(self, frame):
        FrameHandler.handle(frame, self.server, self)

    def handle_connection_requests(self, frame):
        if frame.body[0] == ProtocolInfo.CONNECTION_REQUEST:
            ConnectionRequestHandler.handle(frame.body, self.server, self)
        elif frame.body[0] == ProtocolInfo.NEW_INCOMING_CONNECTION:
            NewIncomingConnectionHandler.handle(frame.body, self.server, self)

    def handle_established_connection(self, frame):
        EstablishedConnectionHandler.handle(frame, self.server, self)

    def process_online_ping(self, frame):
        new_packet_data = OnlinePingHandler.handle(OnlinePing(frame.body), self.server, self)
        self.server.send(new_packet_data, self.address)

    def process_game_packet(self, frame):
        GamePacketHandler.handle(frame.body, self.server, self)

    def handle_disconnect(self, frame_body):
        DisconnectHandler.handle(frame_body, self.server, self)

    def process_unknown_packet(self, frame):
        UnknownPacketHandler.handle(frame.body, self.server, self)

    def send_data(self, data):
        self.server.send(data, self.address)
        self.recovery_queue[self.server_sequence_number] = FrameSetPacket.encode(data)
        self.server_sequence_number += 1

    def handle_frame_set_packet(self, frame_set_packet):
        FrameSetPacket.decode(frame_set_packet, self.server, self)

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
        # Update connection logic (e.g., handle timeouts, resend packets, etc.)
        self.acknowledge()
        self.negative_acknowledge()
