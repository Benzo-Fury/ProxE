import socket
from classes.local.EventEmitter import EventEmitter
from singletons.logger import logger
from threading import Thread
from typing import Literal, Callable, Any
from errno import WSAENOTSOCK  # 10038 on Windows

event_name = Literal[
    "bytes_received",
    "close-request"
]

class Socket(EventEmitter):
    """
        Acts as a wrapper for a TCP socket from the socket module.

        Does not subclass `socket.socket` directly, as this class
        may wrap an existing socket or create a new one dynamically.
    """

    listening: bool # Determines if the socket is currently actively listening for requests
    closed: bool # Determines if this socket has been closed
    
    @property
    def address(self):
        return f"{self.host}:{self.port}"
    
    def __init__(self, existing_socket: socket.socket | None = None, host: str | None = None, port: int = 443):
        # Init
        super().__init__()

        self.listening = False
        self.closed = False

        self.host = host
        self.port = port

        if existing_socket:
            self.base_socket = existing_socket

            peername = existing_socket.getpeername()

            if isinstance(peername, tuple) and len(peername) >= 2:
                self.host, self.port = peername[:2]
            else:
                raise ValueError("Socket peer address is invalid")
        elif host:
            self.base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.base_socket.connect((host, port))
        else:
            raise ValueError("No existing socket or remote hostname provided.")
        
        logger.debug(f"A socket has been created to {self.address}")


    def listen(self):
        if self.listening:
            logger.error(f"Already listening to requests from {self.address}")
            return
        
        self.listening = True
        
        def loop():
            try: 
                while True:
                    if self.closed:
                        break

                    try:
                        data = self.receive() # Blocking - will except when .close() is called
                        logger.debug(f"{len(data)}b worth of data received from {self.address}")
                    except OSError as e:
                        if hasattr(e, "errno") and e.errno == WSAENOTSOCK:
                            self.closed = True
                            logger.debug(f"{self.address} socket closed (WinError 10038), exiting listener")
                            break
                        else:
                            raise

                    if not data:
                        logger.debug(f"{self.address} disconnected gracefully")
                        break # Stops loop - closes socket

                    self.emit("bytes_received", data)
            except Exception as e: 
                logger.error(f"Error listening to {self.address}: {str(e)}")
            finally:
                self.listening = False
                self.emit("close-request")

        Thread(target=loop, daemon=True, name=f"SocketListener-{self.address}").start()

    
    def receive(self, buffer_size: int = 4096) -> bytes:
        """
            Receives data from the socket. Returns up to `buffer_size` bytes.
        """
        if self.closed:
            return b"" # Return nothing, indicates that the socket should be closed locally (its already been closed over the network)

        return self.base_socket.recv(buffer_size)


    def close(self):
        if self.closed:
            logger.debug(f"Socket to {self.address} has already been closed")
            return

        self.closed = True

        if self.base_socket.fileno() != -1:
            logger.debug(f"Closing socket to host {self.address}")
        else:
            logger.debug(f"Socket to host {self.address} was closed prematurely")
        
        try:
            self.base_socket.shutdown(socket.SHUT_WR)
        except: 
            pass

        self.base_socket.close()

    
    def pipe(self, data: bytes, flags = 0):
        """
            Sends all data to the target.
        """

        if self.closed:
            logger.debug(f"Data was sent to a closed socket with address {self.address}")
            return

        try:
            logger.debug(f"Piping {len(data)}b to {self.address}")
            self.base_socket.sendall(data, flags)
        except Exception as e:
            logger.error(f"Pipe error sending to {self.address} - {e}")
            import traceback
            traceback.print_stack()
            raise

    
    def emit(self, event: event_name, *args, **kwargs): 
        EventEmitter.emit(self, event, *args, **kwargs)


    def on(self, event: event_name, listener: Callable[..., Any]): # type: ignore
        EventEmitter.on(self, event, listener)