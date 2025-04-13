from abc import ABC, abstractmethod
from singletons.db import db

class Document(ABC):
    """
        Represents a base TinyDB document. 
        This class can be extended to include additional custom methods.
    """


    @property
    @abstractmethod
    def table_name(self):
        raise NotImplementedError("Should be implemented by sub class.")


    def __init__(self):
        self.id = None  # set on save


    def save(self):
        data = self.to_dict()
        table = db.table(self.table_name)

        if self.id:
            table.update(data, doc_ids=[self.id])
        else:
            self.id = table.insert(data)  # TinyDB returns the doc_id



    def delete(self):
        if self.id:
            db.get_table(self.table_name).remove(doc_ids=[self.id])


    def to_dict(self) -> dict:
        raise NotImplementedError
