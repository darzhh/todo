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
"""dict: Time unit mappings to seconds. Supports s(econds), m(inutes), h(ours), d(ays), w(eeks), y(ears)."""



def parse_date(time) -> timedelta:
    """Parse a human-readable duration string into a timedelta object.
    
    Accepts strings containing one or more '<number><unit>' pairs separated by spaces.
    Supported units: s(econds), m(inutes), h(ours), d(ays), w(eeks), y(ears).
    
    Args:
        time (str): Duration string to parse (e.g., '7d', '1y 2h', '3d 4h 30m').
    
    Returns:
        datetime.timedelta: Total duration represented by the input string.
    
    Raises:
        ValueError: If the input string contains no valid duration patterns.
    
    Examples:
        >>> parse_date('7d')
        timedelta(days=7)
        >>> parse_date('1h 30m')
        timedelta(seconds=5400)
        >>> parse_date('2w')
        timedelta(days=14)
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
    """A todo list manager using TinyDB for persistent storage.
    
    Provides methods to create, read, update, and delete tasks. Tasks include
    unique IDs, descriptions, due dates, and completion status. All data is
    persisted in a JSON file using TinyDB.
    """
    
    def __init__(self):
        """Initialize the Todo manager and connect to the database.
        
        Creates or opens 'todo.json' database file and sets up the console
        for rich table output.
        """
        self.db = TinyDB('todo.json')
        self.item = Query()
        self.console = Console()

    def get_task(self, id):
        """Retrieve the task description for a specific task ID.
        
        Args:
            id (str): Unique identifier of the task.
        
        Returns:
            str: The task description if found, False otherwise.
        
        Examples:
            >>> todo.get_task('abc123')
            'Buy groceries'
        """
        if self.db.search(self.item.id == id):
            return self.db.search(self.item.id == id)[0]['task']
        else:
            return False
             
    def add_task(self, task: str, deadline = "1d") -> None:
        """Add a new task to the todo list with an optional deadline.
        
        Creates a new task record with unique ID, timestamps, and due date.
        
        Args:
            task (str): Description of the task to add.
            deadline (str, optional): Duration until task is due. Defaults to "1d".
                Examples: '7d', '1y 2h', '3d 4h 30m'
        
        Returns:
            None
        
        Examples:
            >>> todo.add_task('Buy milk')
            >>> todo.add_task('Finish report', deadline='3d')
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
        """Delete a task from the todo list permanently.
        
        Args:
            id (str): Unique identifier of the task to delete.
        
        Returns:
            None
        
        Examples:
            >>> todo.delete_task('abc123')
        """
        self.db.remove(self.item.id == id)

    def edit_task(self, id, task) -> None:
        """Update the description of an existing task.
        
        Updates the task description and sets the last_modified timestamp.
        
        Args:
            id (str): Unique identifier of the task to edit.
            task (str): New task description.
        
        Returns:
            None
        
        Examples:
            >>> todo.edit_task('abc123', 'Buy milk and bread')
        """
        self.db.update(
            {
                'task': task,
                'last_modified': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def add_time(self, id, duration = "12h") -> None:
        """Extend the deadline of an existing task by a specified duration.
        
        Adds additional time to a task's due date and updates last_modified timestamp.
        
        Args:
            id (str): Unique identifier of the task.
            duration (str, optional): Time to add to deadline. Defaults to "12h".
                Examples: '2d', '5h', '1w'
        
        Returns:
            None
        
        Examples:
            >>> todo.add_time('abc123', '2d')
            >>> todo.add_time('xyz789')  # Adds 12 hours
        """
        self.db.update(
            {
                'due': self.db.search(self.item.id == id)['due'] + parse_date(duration),
                'last_modified': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def done(self, id) -> None:
        """Mark a task as completed.
        
        Sets the task's done status to True and records the completion timestamp.
        
        Args:
            id (str): Unique identifier of the task to mark as complete.
        
        Returns:
            None
        
        Examples:
            >>> todo.done('abc123')
        """
        self.db.update(
            {
                'done': True,
                'completed_at': round(datetime.now().timestamp())
            },
            self.item.id == id
        )

    def get_pending_tasks(self):
        """Retrieve all incomplete tasks.
        
        Returns:
            list[dict]: List of task dictionaries with done=False.
        
        Examples:
            >>> pending = todo.get_pending_tasks()
            >>> len(pending)
            3
        """
        return self.db.search(self.item.done == False)

    def get_finished_tasks(self):
        """Retrieve all completed tasks.
        
        Returns:
            list[dict]: List of task dictionaries with done=True.
        
        Examples:
            >>> finished = todo.get_finished_tasks()
            >>> len(finished)
            5
        """
        return self.db.search(self.item.done == True)
    
    def get_all_tasks(self):
        """Retrieve all tasks regardless of completion status.
        
        Returns:
            list[dict]: List of all task dictionaries in the database.
        
        Examples:
            >>> all_tasks = todo.get_all_tasks()
            >>> len(all_tasks)
            8
        """
        return self.db.all()
    
    def print_tasks(self, tasks: list) -> None:
        """Display tasks in a formatted pandas DataFrame (legacy method).
        
        Converts Unix timestamps to human-readable datetime objects and displays
        the task list as a pandas DataFrame.
        
        Args:
            tasks (list[dict]): List of task dictionaries to display.
        
        Returns:
            None
        
        Note:
            This method is deprecated. Use updated_print_tasks() instead for
            better formatted output with rich tables.
        
        Examples:
            >>> todo.print_tasks(todo.get_all_tasks())
        """
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
        """Display tasks in a rich formatted table with colors and styling.
        
        Creates a beautifully formatted table showing task details including ID,
        description, due date, completion status, and timestamps. Uses rich
        library for enhanced terminal output.
        
        Args:
            tasks (list[dict]): List of task dictionaries to display.
        
        Returns:
            None
        
        Examples:
            >>> todo.updated_print_tasks(todo.get_pending_tasks())
            >>> todo.updated_print_tasks(todo.get_all_tasks())
        """
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
        """Generate a unique 6-character hexadecimal ID for new tasks.
        
        Continuously generates random IDs until one is found that doesn't
        already exist in the database.
        
        Returns:
            str: A unique 6-character hexadecimal string (e.g., 'a1b2c3').
        
        Examples:
            >>> id = todo.gen_unique_id()
            >>> len(id)
            6
        """
        while self.db.search(self.item.id == id) or id is None:
            id = secrets.token_hex(3)
        return id

class Filters(enum.Enum):
    """Enum for task filtering options in the todo list.
    
    Attributes:
        Pending: Filter to show only incomplete tasks.
        Done: Filter to show only completed tasks.
        All: Filter to show all tasks regardless of status.
    """
    Pending = enum.auto()
    Done = enum.auto()
    All = enum.auto()