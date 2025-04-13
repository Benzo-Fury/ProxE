from socketserver import TCPServer, ThreadingMixIn
from classes.server.Request import Request
import time
import config

from singletons.logger import logger

class Server(ThreadingMixIn, TCPServer):
    """
    Brains of the operation.
    Handles process level logic and information.
    """
    allow_reuse_address = True

    createdAt = time.time()

    def __init__(self):
        super().__init__((config.ip, config.port), Request)

    def serve(self):
        """
        Starts serving the HTTP server.
        Automatically manages the lifecycle and handles shutdown gracefully.
        """
        try:
            logger.info(f"Server starting on IP {config.ip}:{config.port}")
            self.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user.")
        finally:
            logger.info("Shutting down server...")
            self.stop()
            logger.info("Server closed.")

    def stop(self):
        """
        Stops the execution of the proxy.
        """
        self.shutdown()
        self.server_close()