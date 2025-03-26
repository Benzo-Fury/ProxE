from http.server import HTTPServer
from classes.server.ReqHandler import ReqHandler
from classes.local.Logger import Logger
import time
import config

class Server(HTTPServer):
    """
    """
    logger = Logger()
    createdAt = time.time()

    def __init__(self):
        super().__init__((config.ip, config.port), ReqHandler)

    def serve(self):
        """
        Starts serving the HTTP server.
        Automatically manages the lifecycle and handles shutdown gracefully.
        """
        try:
            self.logger.info(f"Server starting on IP {config.ip}:{config.port}")
            self.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user.")
        finally:
            self.logger.info("Shutting down server...")
            self.stop()
            self.logger.info("Server closed.")

    def stop(self):
        """
        Stops the execution of the proxy.
        """
        self.shutdown()
        self.server_close()