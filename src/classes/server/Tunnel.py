class Tunnel:
    """
    Opens a websocket between from client to proxy and proxy to website.
    This allows the proxy to receive data from both ends and pipe it through to the receiver without needing to handle any encryption.
    Therefor it acts like a tunnel just moving bytes between both ends but never handling the data itself.
    """

    client_socket = None
    destination_socket = None

    def __init__(self, remote: str, ):
        # Ensure this class does NOT handle any validation.
        # Is is passed that at this point.
        
        pass
