import socket
import random
import sys
import time
from pieraknet.protocol_info import ProtocolInfo
from pieraknet.packets.offline_ping import OfflinePing
from pieraknet.handlers.offline_ping import OfflinePingHandler


class Server:
    def __init__(self, hostname='0.0.0.0', port='19132'):
        self.hostname = hostname
        self.port = port
        self.ipv = 4
        self.server_name = ''
        self.protocol_version = 11
        self.guid = random.randint(0, sys.maxsize - 1)
        self.connections = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        self.start_time = int(time.time() * 1000)
        self.maxsize = 4096
        self.magic = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.running = True
    
    def get_time_ms(self):
        return int(time.time() * 1000) - self.start_time
    
    def send(self, data, address: tuple):
        if not(data is bytes):
            data = str(data)
            data = data.encode()
        self.socket.sendto(data, (address[0], address[1]))

    def start(self):
        self.socket.bind((self.hostname, self.port))
        while self.running:
            data, client = self.socket.recvfrom(self.maxsize)
            if data[0] == ProtocolInfo.OFFLINE_PING:
                packet = OfflinePing(data)
                OfflinePingHandler.handle(packet, self, client)

    def stop(self):
        self.running = False
        self.socket.close()
