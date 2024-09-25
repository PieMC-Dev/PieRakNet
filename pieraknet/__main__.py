from pieraknet.server import Server

if __name__ == '__main__':
    server = Server(logginglevel = "INFO")
    try:
        server.start()
    except KeyboardInterrupt:
        server.logger.info('Stopping...')
        server.stop()