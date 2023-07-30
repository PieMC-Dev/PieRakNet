import socket
import random
import sys
import time
import logging
from pieraknet.protocol_info import ProtocolInfo
from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.handlers.offline_ping import OfflinePingHandler
from pieraknet.packets.open_connection_request_1 import OpenConnectionRequest1
from pieraknet.handlers.open_connection_request_1 import OpenConnectionRequest1Handler
from pieraknet.packets.open_connection_request_2 import OpenConnectionRequest2
from pieraknet.handlers.open_connection_request_2 import OpenConnectionRequest2Handler


class ConnectionNotFound(Exception):
    pass


class Server:
    def __init__(self, hostname='0.0.0.0', port=19132, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.start_time = round(time.time(), 2)
        self.hostname = hostname
        self.port = port
        self.ipv = 4
        self.name = ''
        self.protocol_version = 11
        self.guid = random.randint(0, sys.maxsize - 1)
        self.connections = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        self.start_time = time.time()
        self.maxsize = 4096
        self.magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.running = False
        self.timeout = 15
        self.logger.info('Server initialized.')

    def get_time_ms(self):
        return round(time.time() - self.start_time, 4)

    def send(self, data, address: tuple):
        if not (isinstance(data, bytes)):
            data = str(data)
            data = data.encode()
        self.socket.sendto(data, address)

    def get_connection(self, address):
        for connection in self.connections:
            if connection.address == address:
                return connection
        raise ConnectionNotFound()

    def add_connection(self, connection):
        self.connections.append(connection)

    def start(self):
        self.running = True
        self.socket.bind((self.hostname, self.port))
        self.logger.info(f"Server started ({str(self.get_time_ms())}s).")
        while self.running:
            time.sleep(1 / 20)
            try:
                data, client = self.socket.recvfrom(self.maxsize)
            except OSError:
                pass
            else:
                if data[0] in [ProtocolInfo.OFFLINE_PING, ProtocolInfo.OFFLINE_PING_OPEN_CONNECTIONS]:
                    packet: OfflinePing = OfflinePing(data)
                    OfflinePingHandler.handle(packet, self, client)
                elif data[0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_1:
                    packet: OpenConnectionRequest1 = OpenConnectionRequest1(data)
                    OpenConnectionRequest1Handler.handle(packet, self, client)
                elif data[0] == ProtocolInfo.OPEN_CONNECTION_REQUEST_2:
                    packet: OpenConnectionRequest2 = OpenConnectionRequest2(data)
                    OpenConnectionRequest2Handler.handle(packet, self, client)
                elif ProtocolInfo.FRAME_SET_0 <= data[0] <= ProtocolInfo.FRAME_SET_F:
                    connection = self.get_connection(client)
                    connection.handle(data)

    def stop(self):
        self.running = False
        self.socket.close()
        self.logger.info('Server stopped.')


if __name__ == '__main__':
    server = Server()
    server.name = 'MCPE;PieMC Server;589;1.20.0;2;20;13253860892328930865;Powered by PieMC;Survival;1;19132;19133;'
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.info('Stopping...')
        server.stop()
