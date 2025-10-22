import sqlite3
from pathlib import Path
from typing import final


@final
class _SqlStorage:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_SqlStorage, cls).__new__(cls)
            cls._instance.db = None
        return cls._instance

    def __init__(self):
        if self.db is None:
            db_path = Path(__file__).parent / 'skylab-data.db'
            self.db = sqlite3.connect(str(db_path))

    def cursor(self):
        return self.db.cursor()
