from socket import socket as tcp_socket
from classes.server.Socket import Socket
from threading import Timer
from time import sleep

from typing import cast, Optional
from _types.HttpMethod import HttpMethod

from singletons.logger import logger

class Tunnel:
    """
        Opens 2 TCP sockets between the client and destination and pipes data between the 2.
        Should not be used for http
    """

    client_socket: Socket
    destination_socket: Socket
    method: HttpMethod

    ended: bool
    timeout_seconds = 10

    def __init__(self, client: tcp_socket | Socket, remote: tcp_socket | Socket | str, method: HttpMethod, existing_buffer: Optional[bytes]):
        """
            Args:
                client: The client in the tunnel.
                remote: The remote server for the tunnel. If hostname/ip is provided, it should be in path format and therefor should include an optional port.
        """
        # Ensure this class does NOT handle any validation.
        # Is is passed that at this point.

        self.ended = False

        if isinstance(client, tcp_socket):
            client = Socket(client)
        # else already a Socket

        if isinstance(remote, tcp_socket):
            remote = Socket(cast(tcp_socket, remote))
        elif isinstance(remote, str):
            host = remote
            port = 443

            if ":" in remote:
                host, port = remote.split(":")
                port = int(port)

            remote = Socket(host=host, port=port)

        self.client_socket = client
        self.destination_socket = remote
        self.existing_buffer = existing_buffer
        self.method = method

        # Starting a timeout
        self.timeout_timer = Timer(self.timeout_seconds, self.terminate)
        self.timeout_timer.daemon = True
        self.timeout_timer.start()

        logger.debug(f"A tunnel has been created between {self.client_socket.address} and {self.destination_socket.address}")

    
    def start(self):
        if self.method == "CONNECT":
            self.client_socket.on("bytes_received", self.destination_socket.pipe)
            self.destination_socket.on("bytes_received", self.client_socket.pipe)

            self.client_socket.on("close-request", self.terminate)
            self.destination_socket.on("close-request", self.terminate)

            self.client_socket.listen()
            self.destination_socket.listen()
        else:
            if not self.existing_buffer:
                logger.error(f"Attempted to pipe empty buffer from {self.client_socket.address} to {self.destination_socket.address} over http")
                return
                
            # Listen for data and pipe back to client
            def byte_received(b: bytes):
                self.client_socket.pipe(b)
                self.terminate()
                
            self.destination_socket.on("bytes_received", byte_received)
            self.destination_socket.listen()
                
            # Pipe existing information to dest
            self.destination_socket.pipe(self.existing_buffer)

        
    def wait_for_resolve(self): 
        while not self.ended:
            sleep(0.3)
        
        return

        
    def terminate(self):
        """
           Terminates both sockets connections.
        """
        if self.ended:
            return
        self.ended = True
        self.client_socket.close()
        self.destination_socket.close()
        logger.debug(f"Terminated tunnel from {self.client_socket.address} to {self.destination_socket.address}")