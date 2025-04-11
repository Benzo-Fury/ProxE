from singletons.TinyDb import db
from typing import Optional

class Document:
    """
        Represents a base TinyDB document. 
        This class can be extended to include additional custom methods.
    """
    table_name: Optional[str] = None  # to be set in subclass

    def __init__(self):
        self.id = None  # set on save
        self.instance = self._get_instance()


    def save(self):
        data = self.to_dict()
        if self.id:
            self.instance.get_table(self.table_name).update(data, doc_ids=[self.id])
        else:
            self.id = self.instance.get_table(self.table_name).insert(data)


    def delete(self):
        if self.id:
            self.instance.get_table(self.table_name).remove(doc_ids=[self.id])


    def to_dict(self) -> dict:
        raise NotImplementedError


    def _get_instance(self):
        if not db:
            raise ValueError
        
        return db
