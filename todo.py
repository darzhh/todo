from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import secrets, string
import pandas as pd
import enum , re
from rich.console import Console
from rich.table import Table


UNITS = {
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 60 * 60 * 24,
    "w": 60 * 60 * 24 * 7,
    "y": 60 * 60 * 24 * 356,
}

"""
Mapping of time unit suffixes to their equivalent duration in seconds.

Keys:
    s: seconds
    m: minutes
    h: hours
    d: days
    w: weeks
    y: years (365 days)
"""



def parse_date(time) -> timedelta:
    """
    Parse a human-readable duration string.

    The function accepts strings containing one or more
    `<number><unit>` pairs separated by spaces.

    Examples:
        "7d"
        "1y 2h"
        "3d 4h 30m"

    Args:
        duration (str): Duration string to parse.

    Returns:
        datetime.timedelta: Total duration represented by the input.

    Raises:
        ValueError: If the input string has an invalid format.

    """

    time = time.lower()
    matches = re.findall(r'(\d+)\s*([smhdwy])', time) # learn
    if not matches:
        raise ValueError("Invalid duration format")

    total_seconds = 0

    for value, unit in matches:
        total_seconds += int(value) * UNITS[unit]
    print(total_seconds)
    return timedelta(seconds=total_seconds)

class Todo():
    def __init__(self):
        self.db = TinyDB('todo.json')
        self.item = Query()
        self.console = Console()

    def get_task(self, id):
        """
        Docstring for get_task
        
        :param self: object
        :param id: id of the task to fetch
        """
        if self.db.search(self.item.id == id):
            return self.db.search(self.item.id == id)[0]['task']
        else:
            return False
             
    def add_task(self, task: str, deadline = "1d") -> None:
        """This functions adds a task to the todo list.

        Args:
            task (str): Task
            deadline (str, optional): Deadline for the task. Defaults to "1d".
        Examples:
            "7d"
            "1y 2h"
            "3d 4h 30m"
        """
        self.db.insert(
            {
                'id': self.gen_unique_id(),
                'task': task,
                'done': False,
                'due': round(datetime.now().timestamp() + parse_date(deadline).total_seconds()),
                'created_at': round(datetime.now().timestamp()),
                'last_modified': round(datetime.now().timestamp()),
                'completed_at': 0
            }
        )

    def delete_task(self, id) -> None:
        """Deletes a task by its id.

        Args:
            id (_type_): ID of the task.
        """
        self.db.remove(self.item.id == id)

    def edit_task(self, id, task) -> None:
        """_summary_

        Args:
            id (_type_): ID of the task
            task (_type_): Task
        """
        self.db.update(
            {
                'task': task,
                'last_modified': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def add_time(self, id, duration = "12h") -> None:
        """Extends the deadline by the given time

        Args:
            id (_type_): ID of the task.
            duration (str, optional): Extended time for the deadline. Defaults to "12h".
        """
        self.db.update(
            {
                'due': self.db.search(self.item.id == id)['due'] + parse_date(duration),
                'last_modified': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def done(self, id) -> None:
        """Marks a task as done.

        Args:
            id (_type_): ID of the task
        """
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
        print(tasks[0])
        print(df)
# {'id': 'c1cc33', 'task': 'hehe new task', 'done': True, 'created_at': 1767955682, 'last_modified': 1767955776, 'completed_at': 1767955866}


    def updated_print_tasks(self, tasks:list) -> None:
        table = Table(title="TODO list")
        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Task", style="magenta")
        table.add_column("Due", justify="left", style="green")
        table.add_column("Completed", justify="left", style="magenta")
        table.add_column("Completed in", justify="left", style="magenta")
        table.add_column("Added at", justify="left", style="rgb(237,178,166)")
        table.add_column("Last Modified at", justify="left", style="rgb(237,178,166)")
#datetime.fromtimestamp
        for task in tasks:
            table.add_row(
                task['id'], 
                task['task'], 
                str(datetime.fromtimestamp(task['due'])), 
                "Yep" if task['done'] else "Nah",
                str(task['completed_at']) if task['completed_at'] else "Due",
                str(datetime.fromtimestamp(task['created_at'])),
                str(datetime.fromtimestamp(task['last_modified'])),
            )
        self.console.print(table)

    print_tasks = updated_print_tasks 

    def gen_unique_id(self):
        id = None
        while self.db.search(self.item.id == id) or id is None:
            id = secrets.token_hex(3)
        return id

class Filters(enum.Enum):
    Pending = enum.auto()
    Done = enum.auto()
    All = enum.auto()