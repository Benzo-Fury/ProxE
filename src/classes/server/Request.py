from socketserver import BaseRequestHandler
from time import sleep
import socket
import select

# Types
from typing import Literal, Optional, cast, Tuple, Dict
from _types.HttpMethod import HttpMethod

# Custom
from classes.server.Tunnel import Tunnel
from classes.server.Socket import Socket
from singletons.logger import logger
import config

from threading import Thread


class Request(BaseRequestHandler):
    """
    Represents a request received 
    """

    def handle(self) -> None:
        buffer = b""

        # Receive request
        while b"\r\n\r\n" not in buffer:
            buffer += self.request.recv(4096)

        # Extract method used
        method, host, path, headers = Request.extract(buffer)
        method = cast(HttpMethod, method)  # e.g., "GET", "POST", etc.

        # Creating client socket
        client_socket = Socket(self.request)
        logger.debug(f"{method} request received from {client_socket.address} aimed at {host}")

        # Creating destination socket
        destination_port = 443 if method == "CONNECT" else 80
        if ":" in host:
            # Overriding default port if one was provided
                host, port_str = host.split(":")
                destination_port = int(port_str)
        destination_socket = Socket(host=host, port=destination_port)

        if method == "CONNECT":
            client_socket.pipe(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        def pipe(src: socket.socket, dst: socket.socket):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                src.close()
                dst.close()

        # Thread(target=pipe, args=(self.request, destination_socket)).start()
        # Thread(target=pipe, args=(destination_socket, self.request)).start()          
                
        # Handle authorization 
        # if config.authorization:
        #     if "authorization" in headers:
        #         # Do some autho stuff
        #     else:
        #         # Pipe back an issue

        # Tunnel will now take control over the sockets and manage them
        t = Tunnel(client_socket, destination_socket, method, buffer)
        t.start()

        # Waiting for tunnel to resolve
        t.wait_for_resolve()

        print(f"Request from {client_socket.address} has resolved")

        
    def finish(self):
        pass  # Prevents auto-closing socket connection. It is now tunnel managed.

    
    @staticmethod
    def extract(data: bytes) -> Tuple[str, str, str, Dict[str, str]]:
        """
        Parses raw HTTP request bytes and returns the method, host, path, and headers.
        
        - For CONNECT requests: host is extracted from the request line.
        - For others: host is extracted from the Host header.
        """
        lines = data.decode(errors="ignore").split("\r\n")

        if not lines or len(lines[0].split()) < 2:
            raise ValueError("Invalid HTTP request line.")

        method, target, *_ = lines[0].split()
        headers: Dict[str, str] = {}

        for line in lines[1:]:
            if not line.strip():
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        if method == "CONNECT":
            host = target  # "example.com:443"
            path = ""      # No path in CONNECT requests
        else:
            host = headers.get("host", "")
            path = target  # Usually "/path?query"

        return method, host, path, headers