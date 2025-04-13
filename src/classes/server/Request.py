from socketserver import BaseRequestHandler
from time import sleep
from base64 import b64decode

# Types
from typing import Literal, Optional, cast, Tuple, Dict
from _types.HttpMethod import HttpMethod

# Custom
from classes.server.Tunnel import Tunnel
from classes.server.Socket import Socket
from classes.db.User import User
from classes.db.AccessLog import AccessLog
from singletons.logger import logger
import config

end = "\r\n\r\n"
responses = {
    "connect-ok": f"HTTP/1.1 200 Connection Established{end}",
    "auth-required": f"HTTP/1.1 407 Proxy Authentication Required\r\nProxy-Authenticate: Basic realm=\"ProxE\"\r\nContent-Length: 0{end}"
}

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

        log: Optional[AccessLog] = None
        if config.usage_logging:
            log = AccessLog(client_socket.address, host, method, "https" if method == "CONNECT" else "http")
        logger.debug(f"{method} request received from {client_socket.address} aimed at {host}")

        # Handle authorization 
        if config.authorization:
            def invalid_auth(reason: Optional[str] = None):
                client_socket.pipe(responses["auth-required"].encode())
                logger.debug(f"Authentication error received from {client_socket.address}: {reason}")
                if log: 
                    log.resolve(reason=reason)

            if "proxy-authorization" in headers:
                auth_header = headers["proxy-authorization"]
                if not auth_header.startswith("Basic "):
                    invalid_auth("Malformed auth header")
                    return
                
                encoded = auth_header.split(" ", 1)[1]
                decoded = b64decode(encoded).decode("utf-8")
                username, password = decoded.split(":", 1)

                user = User.get(username)

                if not user:
                    invalid_auth("Attempted auth user does not exist")
                    return
                
                valid = user.authenticate(password, config.plain_text_passwords)

                if not valid:
                    invalid_auth("Attempted auth password is invalid")
                    return
                
                # User is now authenticated
                if log:
                    log.define_user(user)
            else:
                invalid_auth("No auth header was provided")
                return
            
        if method == "CONNECT":
            client_socket.pipe(responses["connect-ok"].encode())
            
         # Creating destination socket
        destination_port = 443 if method == "CONNECT" else 80
        if ":" in host:
            # Overriding default port if one was provided
                host, port_str = host.split(":")
                destination_port = int(port_str)
        destination_socket = Socket(host=host, port=destination_port)

        # Tunnel will now take control over the sockets and manage them
        t = Tunnel(client_socket, destination_socket, method, buffer)
        t.start()

        # Waiting for tunnel to resolve
        t.wait_for_resolve()

        # Mark access log as resolved
        if log:
            log.resolve(reason="Completed")

        logger.debug(f"Request from {client_socket.address} has resolved")

        
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