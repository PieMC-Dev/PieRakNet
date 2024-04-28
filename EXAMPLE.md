import threading
from pieraknet.server import Server as PieRakNet
from pieraknet.packets.game_packet import GamePacket
from pieraknet.connection import Connection as RakNetConnection
from pieraknet.packets.frame_set import Frame

import logging
import os
import time
import random

class BedrockServer:
    def __init__(self, hostname="0.0.0.0", port=19132, logger=logging.getLogger("PieBedrock"), gamemode="survival", timeout=20):
        self.initialized = False
        self.logger = logger
        self.server_status = None
        self.hostname = hostname
        self.port = port
        self.edition = "MCPE"
        self.protocol_version = 594
        self.version_name = "1.20.12"
        self.name = "PieBedrock Server"
        self.motd = "GitHub/@PieMC-Dev"
        self.players_online = 0
        self.max_players = 20
        self.gamemode_map = {
            "survival": ("Survival", 1),
            "creative": ("Creative", 2),
            "adventure": ("Adventure", 3)
        }
        self.gamemode = self.gamemode_map.get(gamemode, ("Survival", 0))
        self.port_v6 = 19131
        self.guid = random.randint(1, 99999999)
        self.uid = random.randint(1, 99999999)
        self.raknet_version = 11
        self.timeout = timeout
        self.running = False
        self.start_time = int(time.time())
        self.pieraknet_thread = None

    def pieraknet_init(self):
        self.update_server_status()
        self.pieraknet = PieRakNet(self.hostname, self.port, responseData=self.server_status)
        self.pieraknet.timeout = self.timeout
        self.initialized = True

    def get_time_ms(self):
        return round(time.time() - self.start_time, 3)

    def update_server_status(self):
        self.server_status = ";".join([
            self.edition,
            self.name,
            f"{self.protocol_version}",
            self.version_name,
            f"{self.players_online}",
            f"{self.max_players}",
            f"{self.uid}",
            self.motd,
            self.gamemode[0],
            f"{self.gamemode[1]}",
            f"{self.port}",
            f"{self.port_v6}"
        ]) + ";"
        self.server_status

    def start(self):
        if not self.initialized:
            self.pieraknet_init()
        self.running = True
        self.logger.info(f"Running on {self.hostname}:{str(self.port)} ({str(self.get_time_ms())}s).")
        self.pieraknet.start()

    def stop(self):
        self.logger.info("Stopping...")
        self.running = False
        if self.pieraknet_thread:
            self.pieraknet.stop()
            self.pieraknet_thread.join()
        self.logger.info("Stop")

if __name__ == '__main__':
    server = BedrockServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.info('Stopping...')
        server.stop()