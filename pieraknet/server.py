import logging
import random
import socket
import sys
import time

from pieraknet.handlers.offline_ping import OfflinePingHandler
from pieraknet.handlers.open_connection_request_1 import OpenConnectionRequest1Handler
from pieraknet.handlers.open_connection_request_2 import OpenConnectionRequest2Handler
from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.packets.open_connection_request_1 import OpenConnectionRequest1
from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.protocol_info import ProtocolInfo

class ConnectionNotFound(Exception):
    pass

class Server:
    def __init__(self, 
                 hostname='0.0.0.0', 
                 port=19132, 
                 ipv=4, 
                 logger=None, 
                 logginglevel="DEBUG", 
                 game="MCPE", 
                 name="PieRakNet", 
                 game_protocol_version=589, 
                 version_name="1.20.0", 
                 max_player_count=20, 
                 modt="Powered by PieRakNet", 
                 game_mode="survival", 
                 game_mode_number=1, 
                 portv6=19133
                 ):
        if logger is None:
            logger = logging.getLogger("PieRakNet")
            logger.setLevel(getattr(logging, logginglevel.upper()))
            formatter = logging.Formatter('%(asctime)s [%(name)s - %(levelname)s] - %(message)s', "%H:%M:%S")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        self.logger = logger
        self.hostname = hostname
        self.port = port
        self.ipv = ipv
        self.game = game
        self.name = name
        self.game_protocol_version = game_protocol_version
        self.version_name = version_name
        self.player_count = 0
        self.max_player_count = max_player_count
        self.server_id = "13253860892328930866"
        self.modt = modt
        self.game_mode = game_mode
        self.game_mode_number = game_mode_number
        self.portv6 = portv6
        self.raknet_protocol_version = 11
        self.guid = random.randint(0, sys.maxsize - 1)
        self.connections = []
        self.responseData = self.responseDataUpdater()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        self.start_time = time.time()
        self.maxsize = 4096
        self.magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.running = False
        self.timeout = 15
        self.logger.info('Server initialized.')

    def send(self, data, address: tuple):
        if not isinstance(data, bytes):
            self.logger.debug(f"Encoding data to bytes: {data}")
            data = str(data).encode()
        self.logger.debug(f"Sending data to {address}: {data}")
        try:
            self.socket.sendto(data, address)
        except:
            self.logger.error(f"Failed to send data to {address}: {data}")

    def responseDataUpdater(self):
        player_count = len(self.connections)
        self.responseData = f"{self.game};{self.name};{self.game_protocol_version};{self.version_name};{player_count};{self.max_player_count};{self.server_id};{self.modt};{self.game_mode};{self.game_mode_number};{self.portv6};{self.port}"
        # for connection in self.connections:
        #     print(connection)
        # print(self.responseData)
        return self.responseData

    def get_connection(self, address):
        for connection in self.connections:
            if connection.address == address:
                return connection
        raise ConnectionNotFound()

    def add_connection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)
            self.responseDataUpdater()
            self.logger.debug(f"Added connection: {connection} for address {connection.address}")
        else:
            self.logger.warning(f"Connection already exists: {connection.address}")

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            self.responseDataUpdater()
            self.logger.debug(f"Removed connection: {connection} for address {connection.address}")
        else:
            self.logger.warning(f"Connection not found: {connection.address}")

    def get_all_connections(self):
        return self.connections

    def start(self):
        self.running = True
        self.socket.bind((self.hostname, self.port))
        self.logger.info(f"Server started on {self.hostname}:{self.port}!")
        while self.running:
            time.sleep(1 / 20)
            try:
                data, client = self.socket.recvfrom(self.maxsize)
            except OSError as e:
                self.logger.warning(f"OS error while receiving data: {e}")
                continue
            if data:
                self.handle_data(data, client)

    def handle_data(self, data, client):
        print(data)
        if data[0] in {ProtocolInfo.OFFLINE_PING, ProtocolInfo.OFFLINE_PING_OPEN_CONNECTIONS}:
            packet = OfflinePing(data)
            OfflinePingHandler.handle(packet, self, client)
        elif data[0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_1:
            packet = OpenConnectionRequest1(data)
            OpenConnectionRequest1Handler.handle(packet, self, client)
        elif data[0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_2:
            packet = OpenConnectionRequest2(data)
            OpenConnectionRequest2Handler.handle(packet, self, client)
        elif ProtocolInfo.FRAME_SET_0 <= data[0] <= ProtocolInfo.FRAME_SET_F:
            try:
                connection = self.get_connection(client)
                connection.handle(data)
            except ConnectionNotFound:
                self.logger.error(f"Connection not found for address {client}")

    def stop(self):
        self.running = False
        self.socket.close()
        self.logger.info('Server stopped.')
