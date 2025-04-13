from time import time
from typing import Literal, Optional

from classes.db.Document import Document
from classes.db.User import User
from _types.HttpMethod import HttpMethod

class AccessLog(Document):
    """
        Represents an access log of a request made to the proxy.
    """


    @property
    def table_name(self):
        return"access-logs"

    def __init__(self, client_ip: str, destination_ip: str, method: HttpMethod, protocol: Literal["https", "http"], received_at = time()):
        super().__init__()
        self.client_ip = client_ip
        self.destination_ip = destination_ip
        self.method = method
        self.protocol = protocol
        self.received_at = received_at
        self.resolved_at: Optional[float] = None
        self.resolved_reason: Optional[str] = None
        self.resolved = False
        self.user: Optional[str] = None


    def resolve(self, date = time(), reason: Optional[str] = None):
        self.resolved = True
        self.resolved_at = date
        self.resolved_reason = reason
        self.save()

    
    def define_user(self, user: User):
        self.user = user.username


    def to_dict(self) -> dict:
        return {
            key: value
            for key, value in self.__dict__.items()
            if key != "table_name"
        }
