from tinydb import TinyDB, Query
from datetime import datetime
import secrets, string
import pandas as pd
import enum

class Todo():
    def __init__(self):
        self.db = TinyDB('todo.json')
        self.item = Query()

    def get_task(self, id):
        if self.db.search(self.item.id == id):
            return self.db.search(self.item.id == id)[0]['task']
        else:
            return False
             
    def add_task(self, task: str) -> None:
        self.db.insert(
            {
                'id': self.gen_unique_id(),
                'task': task,
                'done': False,
                'created_at': round(datetime.now().timestamp()),
                'last_modified': round(datetime.now().timestamp()),
                'completed_at': 0
            }
        )

    def delete_task(self, id) -> None:
        self.db.remove(self.item.id == id)

    def edit_task(self, id, task) -> None:
        self.db.update(
            {
                'task': task,
                'done': False,
                'last_modified': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def done(self, id) -> None:
        self.db.update(
            {
                'done': True,
                'completed_at': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def get_pending_tasks(self):
        return self.db.search(self.item.done == False)

    def get_finished_tasks(self):
        return self.db.search(self.item.done == True)
    
    def get_all_tasks(self):
        return self.db.all()
    
    def print_tasks(self, tasks: list) -> None:
        df = pd.DataFrame(tasks)
        df["created_at"] = pd.to_datetime(df["created_at"], unit="s")
        df["last_modified"] = pd.to_datetime(df["last_modified"], unit="s")
        df["completed_at"] = pd.to_datetime(
            df["completed_at"],
            unit="s",
            errors="coerce"
        )

        print(df)

    def gen_unique_id(self):
        id = None
        while self.db.search(self.item.id == id) or id is None:
            id = secrets.token_hex(3)
        return id

class Filters(enum.Enum):
    Pending = enum.auto()
    Done = enum.auto()
    All = enum.auto()