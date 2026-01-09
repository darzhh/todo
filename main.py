import click
from todo import Todo as td, Filters

todo = td()

@click.group()
def main():
    pass

@main.group()
def tasks():
    pass

@tasks.command()
@click.argument('task', nargs=-1)
def add(task: str):
    todo.add_task(task = " ".join(task))    
    pass

@tasks.command()
@click.argument('id')
@click.argument('task', nargs=-1)
def edit(id: hex, task: str):
    todo.edit_task(id=id, task = " ".join(task))
    pass

@tasks.command()
@click.argument('id')
def delete(id: hex):
    todo.delete_task(id=id)
    pass

@tasks.command()
@click.argument('id')
def done(id: hex):
    todo.done(id=id)
    pass

@tasks.command()
@click.option('--filter',default=Filters.All, type=click.Choice(Filters, case_sensitive=False))
def view(filter: Filters):
    if filter == Filters.Done:
        todo.print_tasks(todo.get_finished_tasks())
    elif filter == Filters.Pending:
        todo.print_tasks(todo.get_pending_tasks())
    elif filter == Filters.All:
        todo.print_tasks(todo.get_all_tasks())


if __name__ == "__main__":
    main()

