from .server import Server

if __name__ == '__main__':
    server = Server(logginglevel = "INFO")
    server.responseData = "MCPE;PieRakNet Server;589;1.20.0;2;20;13253860892328930865;Powered by PieMC;Survival;1;19132;19133;"
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.info('Stopping...')
        server.stop()