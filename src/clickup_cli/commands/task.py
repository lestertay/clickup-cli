import click
from rich.console import Console

from clickup_cli.helpers import get_client, get_workspace_id, resolve_alias
from clickup_cli.config import load_config
from clickup_cli.formatting import print_task_detail, print_tasks

console = Console()


def _parse_time_estimate(value: str) -> int:
    """Parse a time string (e.g. '2h', '30m', '1h30m') to milliseconds."""
    import re
    match = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?", value)
    if not match or not any(match.groups()):
        console.print(f"[red]Invalid time estimate '{value}'. Use format like '2h', '30m', or '1h30m'.[/red]")
        raise SystemExit(1)
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return (hours * 3600 + minutes * 60) * 1000


@click.group("task")
def task_group():
    """Manage ClickUp tasks!"""
    pass


@task_group.command("list")
@click.option("-l", "--list-id", required=True, help="List ID to show tasks from.")
@click.option("-s", "--status", default=None, help="Filter by status.")
@click.option("-a", "--assignee", default=None, help="Filter by assignee.")
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
@click.argument("task_id", required=False, default=None)
@click.option("-u", "--user", "user_id", default=None, help="User ID to filter by (default: current user).")
def task_view(task_id, user_id):
    """View a task by ID, or list open tasks assigned to a user."""
    client = get_client()
    if task_id:
        if user_id is not None:
            console.print("[yellow]Warning: --user is ignored when a task_id is provided.[/yellow]")
        task = client.get_task(task_id)
        print_task_detail(task)
    else:
        if user_id is None:
            config = load_config()
            user_id = config.get("user_id")
            if user_id is None:
                console.print("[red]user_id not found in config. Run 'cl config init'.[/red]")
                raise SystemExit(1)
            user_id = str(user_id)
        workspace_id = get_workspace_id()
        tasks = client.get_workspace_tasks(workspace_id, user_id)
        print_tasks(tasks)


@task_group.command("create")
@click.option("-l", "--list-id", required=True, help="List ID to create the task in.")
@click.option("-n", "--name", required=True, help="Task name.")
@click.option("-d", "--description", default=None, help="Task description.")
@click.option("-s", "--status", default=None, help="Task status.")
@click.option("-p", "--priority", type=click.Choice(["1", "2", "3", "4"], case_sensitive=False), default=None, help="Priority: 1=urgent, 2=high, 3=normal, 4=low.")
@click.option("-a", "--assignee", default=None, help="Assignee user ID.")
@click.option("-D", "--due-date", default=None, help="Due date (YYYY-MM-DD).")
@click.option("-t", "--tag", multiple=True, help="Tag(s) to add.")
@click.option("-T", "--time-estimate", default=None, help="Time estimate (e.g. 2h, 30m, 1h30m).")
def task_create(list_id, name, description, status, priority, assignee, due_date, tag, time_estimate):
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
    if time_estimate:
        task_data["time_estimate"] = _parse_time_estimate(time_estimate)

    task = client.create_task(list_id, task_data)
    console.print(f"[green]Task created: {task.name} ({task.id})[/green]")


@task_group.command("update")
@click.argument("task_id")
@click.option("-n", "--name", default=None, help="New task name.")
@click.option("-d", "--description", default=None, help="New description.")
@click.option("-s", "--status", default=None, help="New status.")
@click.option("-p", "--priority", type=click.Choice(["1", "2", "3", "4"], case_sensitive=False), default=None, help="Priority: 1=urgent, 2=high, 3=normal, 4=low.")
@click.option("-a", "--assignee", default=None, help="Assignee user ID to add.")
@click.option("-D", "--due-date", default=None, help="Due date (YYYY-MM-DD).")
@click.option("-t", "--tag", multiple=True, help="Tag(s) to set.")
@click.option("-T", "--time-estimate", default=None, help="Time estimate (e.g. 2h, 30m, 1h30m).")
def task_update(task_id, name, description, status, priority, assignee, due_date, tag, time_estimate):
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
    if time_estimate:
        task_data["time_estimate"] = _parse_time_estimate(time_estimate)

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
