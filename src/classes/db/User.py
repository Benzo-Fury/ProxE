from bcrypt import checkpw
from tinydb import Query

from classes.db.Document import Document
from singletons.db import db

class User(Document):
    """
        Extends the document class and represents a user stored in the db.
    """

    @property
    def table_name(self):
        return"users"

    def __init__(self, username: str, hash: str):
        super().__init__()
        self.username = username
        self.hash = hash


    def authenticate(self, pas: str, ptm = False):
        if ptm:
            return pas == self.hash
        else: 
            try:
                return checkpw(pas.encode(), self.hash.encode())
            except ValueError:
                return False  # Invalid bcrypt hash format
            
    
    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.hash,
        }
    

    @classmethod
    def from_dict(cls, data: dict):
        if not "username" in data or not "password" in data:
            raise ValueError

        return cls(
            data["username"],
            data["password"]
        )
    

    @staticmethod
    def get(username: str):
        table = db.table("users")

        u = table.get(Query().username == username)

        if not u:
            return None
        
        if isinstance(u, list):
            raise Exception(f"Multiple users were returned with username: {username}")
        
        return User.from_dict(dict(u))