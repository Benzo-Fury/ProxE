from socket import socket as tcp_socket

class Socket:
    """
    Acts as a wrapper for the a TCP socket provided in the socket module.
    Doesn't extend it as we need to sometimes take existing sockets and convert them into one of these.
    """
    base_socket: tcp_socket

    def __init__(self, existing_socket: tcp_socket | None = None, hostname: str | None = None):
        if existing_socket:
            self.base_socket = existing_socket
        elif hostname:
            # Create a base socket here
            pass
        else:
            raise ValueError("No existing socket or remote hostname provided.")