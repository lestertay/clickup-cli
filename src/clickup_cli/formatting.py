from rich.console import Console
from rich.table import Table

from clickup_cli.models import Folder, Space, Task, TaskList

console = Console()

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
    table.add_column("Tags")

    for t in tasks:
        priority_style = PRIORITY_COLORS.get(t.priority or "", "")
        table.add_row(
            t.id,
            t.name,
            t.status,
            f"[{priority_style}]{t.priority or '-'}[/{priority_style}]" if priority_style else (t.priority or "-"),
            ", ".join(t.assignees) or "-",
            t.due_date or "-",
            ", ".join(t.tags) or "-",
        )

    console.print(table)


def print_task_detail(task: Task) -> None:
    console.print(f"\n[bold]{task.name}[/bold]  [dim]({task.id})[/dim]")
    console.print(f"  Status:    {task.status}")
    console.print(f"  Priority:  {task.priority or '-'}")
    console.print(f"  Assignees: {', '.join(task.assignees) or '-'}")
    console.print(f"  Due Date:  {task.due_date or '-'}")
    console.print(f"  Tags:      {', '.join(task.tags) or '-'}")
    if task.description:
        console.print(f"\n  {task.description}")
    if task.url:
        console.print(f"\n  [link={task.url}]{task.url}[/link]")
    console.print()
