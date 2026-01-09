"""Todo CLI Application

A command-line interface for managing a todo list with support for:
- Adding tasks with deadlines
- Editing task descriptions and deadlines
- Marking tasks as complete
- Deleting tasks
- Viewing tasks with filters (all, pending, completed)
"""

import click
from todo import Todo as td, Filters

todo = td()

@click.group()
def tasks():
    """Main CLI group for todo operations."""
    pass

@tasks.command()
@click.option('--deadline', default="1d")
@click.argument('task', nargs=-1)
def add(deadline, task: str):
    """Add a new task to the todo list.
    
    Args:
        deadline: Duration until task is due (e.g., '1d', '2h', '1w'). Defaults to '1d'.
        task: Task description (can be multiple words).
    
    Examples:
        tasks add "Buy groceries"
        tasks add --deadline 3d "Complete project report"
    """
    todo.add_task(task = " ".join(task), deadline=deadline)

@tasks.group()
def edit():
    """Group of commands for editing existing tasks."""
    pass

@edit.command()
@click.argument('id')
@click.argument('task', nargs=-1)
def task(id: hex, task: str):
    """Edit the description of an existing task.
    
    Args:
        id: Unique identifier of the task to edit.
        task: New task description (can be multiple words).
    
    Examples:
        tasks edit task abc123 "Updated task description"
    """
    todo.edit_task(id=id, task = " ".join(task))

@edit.command()
@click.argument('id')
@click.argument('duration')
def deadline(id: hex, duration):
    """Extend the deadline of an existing task.
    
    Args:
        id: Unique identifier of the task.
        duration: Additional time to add to the deadline (e.g., '2d', '5h').
    
    Examples:
        tasks edit deadline abc123 2d
        tasks edit deadline xyz789 12h
    """
    todo.add_time(id, duration)

@tasks.command()
@click.argument('id')
def delete(id: hex):
    """Delete a task from the todo list.
    
    Args:
        id: Unique identifier of the task to delete.
    
    Examples:
        tasks delete abc123
    """
    todo.delete_task(id=id)

@tasks.command()
@click.argument('id')
def done(id: hex):
    """Mark a task as completed.
    
    Args:
        id: Unique identifier of the task to mark as done.
    
    Examples:
        tasks done abc123
    """
    todo.done(id=id)

@tasks.command()
@click.option('--filter',default=Filters.All, type=click.Choice(Filters, case_sensitive=False))
def view(filter: Filters):
    """Display tasks with optional filtering.
    
    Args:
        filter: Filter type - 'all' (default), 'pending', or 'done'.
            - all: Display all tasks
            - pending: Display incomplete tasks only
            - done: Display completed tasks only
    
    Examples:
        tasks view
        tasks view --filter pending
        tasks view --filter done
    """
    if filter == Filters.Done:
        todo.print_tasks(todo.get_finished_tasks())
    elif filter == Filters.Pending:
        todo.print_tasks(todo.get_pending_tasks())
    elif filter == Filters.All:
        todo.print_tasks(todo.get_all_tasks())


if __name__ == "__main__":
    tasks()

