from datetime import datetime
from sqlite3 import Row


class Writer(dict):
    def __init__(self, record: Row):
        self.id: str = record["uid"]
        self.handle: str = record["handle"]
        self.date: datetime = datetime.fromisoformat(record["date"])

        # Make the class JSON serializable
        super().__init__(self.__dict__)
