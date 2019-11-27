from datetime import date
from sqlite3 import Row
from typing import Optional


class Prompt(dict):
    def __init__(self, record: Row):
        self.id: str = record["tweet_id"]
        self.date: date = date.fromisoformat(record["date"])
        self.content: str = record["content"]
        self.word: str = record["word"]
        self.media: Optional[str] = record["media"]
        self.writer_id: str = record["uid"]
        self.writer_handle: str = record["writer_handle"]

        # We don't need the record anymore
        del record

        # Make the class JSON serializable
        super().__init__(self.__dict__)