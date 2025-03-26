from http.server import BaseHTTPRequestHandler
from typing import Optional
import json as json_lib # Avoiding naming issues
import http.client
from urllib.parse import urlsplit
from classes.server.Socket import Socket
import config

class ReqHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Checking if http is enabled
        if config.disable_http_traffic:
            self.respond(403, text="HTTP traffic has been disabled on this server.")
            return
        
        # Extracting host from headers
        host = self.headers.get("Host")
        if not host:
            self.error(400, "Bad request: Host header is missing.")
            return
        
        # Make connection and forward request
        connection = http.client.HTTPConnection(host)

        url = urlsplit(self.path)
        path = url.path or "/"
        if url.query:
            path += "?" + url.query 

        connection.request("GET", path, headers=dict(self.headers))

        # Accept the response
        res = connection.getresponse()

        # Send everything back
        body = res.read()
        self.send_response(res.status)
        for k, v in res.getheaders():
            if k.lower() not in ("content-length", "transfer-encoding", "connection"):
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)   

        
    def do_CONNECT(self):
        # TO IMPLEMENT 
        pass
        # Authorize

        # Create the socket
        # socket = Socket(self.connection)

        # Respond to the connection with status 200 as utf-8 encoded
        # self.wfile.write("HTTP/1.1 200 Connection Established\r\n\r\n".encode())

        # 


        # self.headers can be used for authorization
        # self.connection is the clients socket... consider using this to create an instanced socket class
        # self.rfile is how we can read information from the client
        # self.wfile is how we can send information to the client.
        # self.path is the target ip and port


    # ------------------ Response Methods ------------------ #


    def respond(
        self, 
        code: int,
        text: Optional[str] = None, 
        json: Optional[dict] = None,
        headers: Optional[dict] = None
    ):
        self.send_response(code)

        # Headers
        if json is not None:
            body = json_lib.dumps(json)
            self.send_header("Content-Type", "application/json")
        elif text is not None:
            body = text
            self.send_header("Content-Type", "text/plain")
        else:
            body = ""
            self.send_header("Content-Type", "text/plain")

        self.send_header("Content-Length", str(len(body.encode())))

        if headers:
            for key, value in headers.items():
                self.send_header(key, value)

        self.end_headers()

        # Body
        self.wfile.write(body.encode())

    
    def error(self, code: int, msg: Optional[str] = None):
        self.send_error(code, msg)
