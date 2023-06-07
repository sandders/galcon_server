from tcp_handler import TCPHandler

if __name__ == '__main__':
    try:
        server = TCPHandler('config.json')
        server.start()
        print("Server started successfully.")
        print("Press Ctrl+C to stop the server.")
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped.")
