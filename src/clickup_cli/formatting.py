from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table

from clickup_cli.models import Folder, Space, Task, TaskList

console = Console()


def _format_due_date(due_date: str | None) -> str:
    """Convert Unix timestamp (ms) to local human-readable date."""
    if not due_date:
        return "-"
    try:
        ts = int(due_date) / 1000
        dt = datetime.fromtimestamp(ts).astimezone()
        return dt.strftime("%m-%d %H:%M")
    except (ValueError, OSError):
        return due_date


def _format_time_estimate(ms: int | None) -> str:
    """Convert milliseconds to human-readable time string."""
    if not ms:
        return "-"
    total_minutes = ms // 60000
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours}h{minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"


PRIORITY_COLORS = {
    "urgent": "red",
    "high": "yellow",
    "normal": "blue",
    "low": "dim",
}


def print_spaces(spaces: list[Space]) -> None:
    table = Table(title="Spaces")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    for s in spaces:
        table.add_row(s.id, s.name)
    console.print(table)


def print_folders(folders: list[Folder]) -> None:
    table = Table(title="Folders")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    for f in folders:
        table.add_row(f.id, f.name)
    console.print(table)


def print_lists(lists: list[TaskList]) -> None:
    table = Table(title="Lists")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    for l in lists:
        table.add_row(l.id, l.name)
    console.print(table)


def print_tasks(tasks: list[Task]) -> None:
    table = Table(title="Tasks")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Assignees")
    table.add_column("Due Date")
    table.add_column("Estimate")
    table.add_column("Tags")

    for t in tasks:
        priority_style = PRIORITY_COLORS.get(t.priority or "", "")
        table.add_row(
            t.id,
            t.name,
            t.status,
            f"[{priority_style}]{t.priority or '-'}[/{priority_style}]" if priority_style else (t.priority or "-"),
            ", ".join(t.assignees) or "-",
            _format_due_date(t.due_date),
            _format_time_estimate(t.time_estimate),
            ", ".join(t.tags) or "-",
        )

    console.print(table)


def print_task_detail(task: Task) -> None:
    console.print(f"\n[bold]{task.name}[/bold]  [dim]({task.id})[/dim]")
    console.print(f"  Status:    {task.status}")
    console.print(f"  Priority:  {task.priority or '-'}")
    console.print(f"  Assignees: {', '.join(task.assignees) or '-'}")
    console.print(f"  Due Date:  {_format_due_date(task.due_date)}")
    console.print(f"  Estimate:  {_format_time_estimate(task.time_estimate)}")
    console.print(f"  Tags:      {', '.join(task.tags) or '-'}")
    if task.description:
        console.print(f"\n  {task.description}")
    if task.url:
        console.print(f"\n  [link={task.url}]{task.url}[/link]")
    console.print()
