import socket
import random
import sys


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
