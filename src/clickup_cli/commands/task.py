import click
from rich.console import Console

from clickup_cli.helpers import get_client, resolve_alias
from clickup_cli.formatting import print_task_detail, print_tasks

console = Console()


@click.group("task")
def task_group():
    """Manage ClickUp tasks!"""
    pass


@task_group.command("list")
@click.option("--list-id", required=True, help="List ID to show tasks from.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--assignee", default=None, help="Filter by assignee.")
def task_list(list_id, status, assignee):
    """List tasks in a ClickUp list."""
    list_id = resolve_alias(list_id, "list")
    client = get_client()
    filters = {}
    if status:
        filters["statuses"] = [status]
    if assignee:
        filters["assignees"] = [assignee]
    tasks = client.list_tasks(list_id, **filters)
    print_tasks(tasks)


@task_group.command("view")
@click.argument("task_id")
def task_view(task_id):
    """View a single task's details."""
    client = get_client()
    task = client.get_task(task_id)
    print_task_detail(task)


@task_group.command("create")
@click.option("--list-id", required=True, help="List ID to create the task in.")
@click.option("--name", required=True, help="Task name.")
@click.option("--description", default=None, help="Task description.")
@click.option("--status", default=None, help="Task status.")
@click.option("--priority", type=click.Choice(["1", "2", "3", "4"], case_sensitive=False), default=None, help="Priority: 1=urgent, 2=high, 3=normal, 4=low.")
@click.option("--assignee", default=None, help="Assignee user ID.")
@click.option("--due-date", default=None, help="Due date (YYYY-MM-DD).")
@click.option("--tag", multiple=True, help="Tag(s) to add.")
def task_create(list_id, name, description, status, priority, assignee, due_date, tag):
    """Create a new task."""
    list_id = resolve_alias(list_id, "list")
    client = get_client()
    task_data = {"name": name}
    if description:
        task_data["description"] = description
    if status:
        task_data["status"] = status
    if priority:
        task_data["priority"] = int(priority)
    if assignee:
        task_data["assignees"] = [int(assignee)]
    if due_date:
        from datetime import datetime

        dt = datetime.strptime(due_date, "%Y-%m-%d")
        task_data["due_date"] = int(dt.timestamp() * 1000)
    if tag:
        task_data["tags"] = list(tag)

    task = client.create_task(list_id, task_data)
    console.print(f"[green]Task created: {task.name} ({task.id})[/green]")


@task_group.command("update")
@click.argument("task_id")
@click.option("--name", default=None, help="New task name.")
@click.option("--description", default=None, help="New description.")
@click.option("--status", default=None, help="New status.")
@click.option("--priority", type=click.Choice(["1", "2", "3", "4"], case_sensitive=False), default=None, help="Priority: 1=urgent, 2=high, 3=normal, 4=low.")
@click.option("--assignee", default=None, help="Assignee user ID to add.")
@click.option("--due-date", default=None, help="Due date (YYYY-MM-DD).")
@click.option("--tag", multiple=True, help="Tag(s) to set.")
def task_update(task_id, name, description, status, priority, assignee, due_date, tag):
    """Update an existing task."""
    client = get_client()
    task_data = {}
    if name:
        task_data["name"] = name
    if description:
        task_data["description"] = description
    if status:
        task_data["status"] = status
    if priority:
        task_data["priority"] = int(priority)
    if assignee:
        task_data["assignees"] = {"add": [int(assignee)]}
    if due_date:
        from datetime import datetime

        dt = datetime.strptime(due_date, "%Y-%m-%d")
        task_data["due_date"] = int(dt.timestamp() * 1000)
    if tag:
        task_data["tags"] = list(tag)

    if not task_data:
        console.print("[yellow]No updates specified.[/yellow]")
        return

    task = client.update_task(task_id, task_data)
    console.print(f"[green]Task updated: {task.name} ({task.id})[/green]")


@task_group.command("delete")
@click.argument("task_id")
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def task_delete(task_id):
    """Delete a task."""
    client = get_client()
    client.delete_task(task_id)
    console.print(f"[green]Task {task_id} deleted.[/green]")
