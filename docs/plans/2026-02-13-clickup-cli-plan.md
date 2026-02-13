# ClickUp CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that manages ClickUp tasks through the full workspace hierarchy (Spaces > Folders > Lists > Tasks).

**Architecture:** Flat Click command groups (`clickup <resource> <action>`) backed by an httpx-based API client, with Rich table output and YAML config for auth.

**Tech Stack:** Python, uv, Click, httpx, Rich, PyYAML

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/clickup_cli/__init__.py`
- Create: `src/clickup_cli/cli.py`

**Step 1: Initialize uv project**

```bash
cd /Users/lestertay/clickup-cli
uv init --lib --name clickup-cli
```

Remove the auto-generated `src/clickup_cli/py.typed` if created. Remove auto-generated `hello` function from `__init__.py`.

**Step 2: Configure pyproject.toml**

Ensure `pyproject.toml` has:

```toml
[project]
name = "clickup-cli"
version = "0.1.0"
description = "CLI tool for managing ClickUp tasks"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "httpx>=0.27",
    "rich>=13.0",
    "pyyaml>=6.0",
]

[project.scripts]
clickup = "clickup_cli.cli:cli"
```

**Step 3: Install dependencies**

```bash
uv add click httpx rich pyyaml
```

**Step 4: Create CLI entry point**

`src/clickup_cli/cli.py`:

```python
import click


@click.group()
@click.version_option()
def cli():
    """CLI tool for managing ClickUp tasks."""
    pass
```

`src/clickup_cli/__init__.py`:

```python
"""ClickUp CLI - manage your ClickUp tasks from the terminal."""
```

**Step 5: Verify it runs**

```bash
uv run clickup --help
```

Expected: Shows help text with version option.

**Step 6: Commit**

```bash
git add pyproject.toml uv.lock src/
git commit -m "feat: scaffold project with uv, Click entry point"
```

---

### Task 2: Config Module

**Files:**
- Create: `src/clickup_cli/config.py`
- Create: `src/clickup_cli/commands/config_cmd.py`
- Create: `src/clickup_cli/commands/__init__.py`
- Modify: `src/clickup_cli/cli.py`

**Step 1: Create config module**

`src/clickup_cli/config.py`:

```python
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".clickup-cli"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config() -> dict:
    """Load config from ~/.clickup-cli/config.yaml."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config not found at {CONFIG_FILE}. Run 'clickup config init' to set up."
        )
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    if not config or "api_token" not in config:
        raise ValueError(
            "Config is missing 'api_token'. Run 'clickup config init' to fix."
        )
    return config


def save_config(config: dict) -> None:
    """Save config to ~/.clickup-cli/config.yaml."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
```

**Step 2: Create config commands**

`src/clickup_cli/commands/__init__.py`:

```python
```

`src/clickup_cli/commands/config_cmd.py`:

```python
import click
from rich.console import Console
from rich.table import Table

from clickup_cli.config import CONFIG_FILE, load_config, save_config

console = Console()


@click.group("config")
def config_group():
    """Manage CLI configuration."""
    pass


@config_group.command("init")
def config_init():
    """Set up ClickUp CLI configuration."""
    api_token = click.prompt("Enter your ClickUp API token", hide_input=True)
    config = {"api_token": api_token}
    save_config(config)
    console.print(f"[green]Config saved to {CONFIG_FILE}[/green]")


@config_group.command("show")
def config_show():
    """Display current configuration."""
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)

    table = Table(title="ClickUp CLI Config")
    table.add_column("Key", style="bold")
    table.add_column("Value")

    for key, value in config.items():
        display_value = value
        if key == "api_token":
            display_value = value[:8] + "..." if len(value) > 8 else "***"
        table.add_row(key, str(display_value))

    console.print(table)
```

**Step 3: Register config group in cli.py**

Update `src/clickup_cli/cli.py`:

```python
import click

from clickup_cli.commands.config_cmd import config_group


@click.group()
@click.version_option()
def cli():
    """CLI tool for managing ClickUp tasks."""
    pass


cli.add_command(config_group)
```

**Step 4: Verify**

```bash
uv run clickup config --help
```

**Step 5: Commit**

```bash
git add src/clickup_cli/config.py src/clickup_cli/commands/
git commit -m "feat: add config module with init and show commands"
```

---

### Task 3: Models

**Files:**
- Create: `src/clickup_cli/models.py`

**Step 1: Create dataclasses**

`src/clickup_cli/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Space:
    id: str
    name: str

    @classmethod
    def from_api(cls, data: dict) -> Space:
        return cls(id=data["id"], name=data["name"])


@dataclass
class Folder:
    id: str
    name: str
    space_id: str

    @classmethod
    def from_api(cls, data: dict) -> Folder:
        return cls(
            id=data["id"],
            name=data["name"],
            space_id=data.get("space", {}).get("id", ""),
        )


@dataclass
class TaskList:
    id: str
    name: str
    folder_id: str

    @classmethod
    def from_api(cls, data: dict) -> TaskList:
        return cls(
            id=data["id"],
            name=data["name"],
            folder_id=data.get("folder", {}).get("id", ""),
        )


@dataclass
class Task:
    id: str
    name: str
    status: str
    assignees: list[str] = field(default_factory=list)
    priority: str | None = None
    due_date: str | None = None
    tags: list[str] = field(default_factory=list)
    description: str = ""
    url: str = ""
    list_id: str = ""

    @classmethod
    def from_api(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            status=data.get("status", {}).get("status", ""),
            assignees=[a.get("username", a.get("email", "")) for a in data.get("assignees", [])],
            priority=data.get("priority", {}).get("priority") if data.get("priority") else None,
            due_date=data.get("due_date"),
            tags=[t["name"] for t in data.get("tags", [])],
            description=data.get("description", ""),
            url=data.get("url", ""),
            list_id=data.get("list", {}).get("id", ""),
        )
```

**Step 2: Commit**

```bash
git add src/clickup_cli/models.py
git commit -m "feat: add dataclass models for Space, Folder, TaskList, Task"
```

---

### Task 4: API Client

**Files:**
- Create: `src/clickup_cli/client.py`

**Step 1: Create API client**

`src/clickup_cli/client.py`:

```python
from __future__ import annotations

import sys

import httpx
from rich.console import Console

from clickup_cli.models import Folder, Space, Task, TaskList

console = Console()

BASE_URL = "https://api.clickup.com/api/v2"


class ClickUpClient:
    def __init__(self, api_token: str):
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": api_token},
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.ConnectError:
            console.print("[red]Could not reach ClickUp API. Check your connection.[/red]")
            sys.exit(1)

        if response.status_code == 401:
            console.print("[red]Authentication failed. Check your API token (clickup config init).[/red]")
            sys.exit(1)
        if response.status_code == 404:
            console.print(f"[red]Resource not found: {path}[/red]")
            sys.exit(1)
        if response.status_code == 429:
            console.print("[red]Rate limited by ClickUp API. Wait a moment and try again.[/red]")
            sys.exit(1)
        if response.status_code >= 400:
            console.print(f"[red]API error ({response.status_code}): {response.text}[/red]")
            sys.exit(1)

        return response.json()

    # -- Workspaces / Teams --

    def get_teams(self) -> list[dict]:
        data = self._request("GET", "/team")
        return data.get("teams", [])

    # -- Spaces --

    def list_spaces(self, team_id: str) -> list[Space]:
        data = self._request("GET", f"/team/{team_id}/space")
        return [Space.from_api(s) for s in data.get("spaces", [])]

    # -- Folders --

    def list_folders(self, space_id: str) -> list[Folder]:
        data = self._request("GET", f"/space/{space_id}/folder")
        return [Folder.from_api(f) for f in data.get("folders", [])]

    # -- Lists --

    def list_lists(self, folder_id: str) -> list[TaskList]:
        data = self._request("GET", f"/folder/{folder_id}/list")
        return [TaskList.from_api(l) for l in data.get("lists", [])]

    def list_folderless_lists(self, space_id: str) -> list[TaskList]:
        data = self._request("GET", f"/space/{space_id}/list")
        return [TaskList.from_api(l) for l in data.get("lists", [])]

    # -- Tasks --

    def list_tasks(self, list_id: str, **filters) -> list[Task]:
        params = {}
        if "statuses" in filters:
            params["statuses[]"] = filters["statuses"]
        if "assignees" in filters:
            params["assignees[]"] = filters["assignees"]
        data = self._request("GET", f"/list/{list_id}/task", params=params)
        return [Task.from_api(t) for t in data.get("tasks", [])]

    def get_task(self, task_id: str) -> Task:
        data = self._request("GET", f"/task/{task_id}")
        return Task.from_api(data)

    def create_task(self, list_id: str, task_data: dict) -> Task:
        data = self._request("POST", f"/list/{list_id}/task", json=task_data)
        return Task.from_api(data)

    def update_task(self, task_id: str, task_data: dict) -> Task:
        data = self._request("PUT", f"/task/{task_id}", json=task_data)
        return Task.from_api(data)

    def delete_task(self, task_id: str) -> None:
        self._request("DELETE", f"/task/{task_id}")
```

**Step 2: Commit**

```bash
git add src/clickup_cli/client.py
git commit -m "feat: add ClickUp API client with full CRUD support"
```

---

### Task 5: Formatting Module

**Files:**
- Create: `src/clickup_cli/formatting.py`

**Step 1: Create Rich table formatters**

`src/clickup_cli/formatting.py`:

```python
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
```

**Step 2: Commit**

```bash
git add src/clickup_cli/formatting.py
git commit -m "feat: add Rich table formatting for all resource types"
```

---

### Task 6: Helper — Client from Config

**Files:**
- Modify: `src/clickup_cli/cli.py`

**Step 1: Add helper to create client from config**

Update `src/clickup_cli/cli.py` to pass client via Click context:

```python
import click
from rich.console import Console

from clickup_cli.client import ClickUpClient
from clickup_cli.commands.config_cmd import config_group
from clickup_cli.config import load_config

console = Console()


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """CLI tool for managing ClickUp tasks."""
    ctx.ensure_object(dict)


def get_client() -> ClickUpClient:
    """Load config and return an authenticated ClickUp client."""
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    return ClickUpClient(config["api_token"])


def get_workspace_id() -> str:
    """Load workspace_id from config."""
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]{e}[/red]")
        raise SystemExit(1)
    wid = config.get("workspace_id")
    if not wid:
        console.print("[red]No workspace_id in config. Run 'clickup config init'.[/red]")
        raise SystemExit(1)
    return wid


cli.add_command(config_group)
```

**Step 2: Update config init to fetch and store workspace_id**

In `src/clickup_cli/commands/config_cmd.py`, update `config_init`:

```python
@config_group.command("init")
def config_init():
    """Set up ClickUp CLI configuration."""
    api_token = click.prompt("Enter your ClickUp API token", hide_input=True)

    # Fetch workspace
    from clickup_cli.client import ClickUpClient

    client = ClickUpClient(api_token)
    teams = client.get_teams()

    if not teams:
        console.print("[red]No workspaces found for this token.[/red]")
        raise SystemExit(1)

    if len(teams) == 1:
        workspace = teams[0]
        console.print(f"Using workspace: [bold]{workspace['name']}[/bold]")
    else:
        console.print("Available workspaces:")
        for i, t in enumerate(teams, 1):
            console.print(f"  {i}. {t['name']}")
        choice = click.prompt("Select workspace", type=int, default=1)
        workspace = teams[choice - 1]

    config = {
        "api_token": api_token,
        "workspace_id": workspace["id"],
        "workspace_name": workspace["name"],
    }
    save_config(config)
    console.print(f"[green]Config saved to {CONFIG_FILE}[/green]")
```

**Step 3: Commit**

```bash
git add src/clickup_cli/cli.py src/clickup_cli/commands/config_cmd.py
git commit -m "feat: add client helper and workspace auto-detection in config init"
```

---

### Task 7: Space Commands

**Files:**
- Create: `src/clickup_cli/commands/space.py`
- Modify: `src/clickup_cli/cli.py`

**Step 1: Create space commands**

`src/clickup_cli/commands/space.py`:

```python
import click

from clickup_cli.cli import get_client, get_workspace_id
from clickup_cli.formatting import print_spaces


@click.group("space")
def space_group():
    """Manage ClickUp spaces."""
    pass


@space_group.command("list")
def space_list():
    """List all spaces in the workspace."""
    client = get_client()
    workspace_id = get_workspace_id()
    spaces = client.list_spaces(workspace_id)
    print_spaces(spaces)
```

**Step 2: Register in cli.py**

Add to `src/clickup_cli/cli.py`:

```python
from clickup_cli.commands.space import space_group
cli.add_command(space_group)
```

**Step 3: Commit**

```bash
git add src/clickup_cli/commands/space.py src/clickup_cli/cli.py
git commit -m "feat: add space list command"
```

---

### Task 8: Folder Commands

**Files:**
- Create: `src/clickup_cli/commands/folder.py`
- Modify: `src/clickup_cli/cli.py`

**Step 1: Create folder commands**

`src/clickup_cli/commands/folder.py`:

```python
import click
from rich.console import Console

from clickup_cli.cli import get_client, get_workspace_id
from clickup_cli.formatting import print_folders

console = Console()


@click.group("folder")
def folder_group():
    """Manage ClickUp folders."""
    pass


@folder_group.command("list")
@click.option("--space-id", default=None, help="Space ID to list folders from.")
def folder_list(space_id):
    """List folders in a space."""
    client = get_client()

    if not space_id:
        workspace_id = get_workspace_id()
        spaces = client.list_spaces(workspace_id)
        if not spaces:
            console.print("[red]No spaces found.[/red]")
            raise SystemExit(1)
        for i, s in enumerate(spaces, 1):
            console.print(f"  {i}. {s.name} ({s.id})")
        choice = click.prompt("Select space", type=int, default=1)
        space_id = spaces[choice - 1].id

    folders = client.list_folders(space_id)
    print_folders(folders)
```

**Step 2: Register in cli.py**

```python
from clickup_cli.commands.folder import folder_group
cli.add_command(folder_group)
```

**Step 3: Commit**

```bash
git add src/clickup_cli/commands/folder.py src/clickup_cli/cli.py
git commit -m "feat: add folder list command with interactive space selection"
```

---

### Task 9: List Commands

**Files:**
- Create: `src/clickup_cli/commands/list.py`
- Modify: `src/clickup_cli/cli.py`

**Step 1: Create list commands**

`src/clickup_cli/commands/list.py`:

```python
import click
from rich.console import Console

from clickup_cli.cli import get_client, get_workspace_id
from clickup_cli.formatting import print_lists

console = Console()


@click.group("list")
def list_group():
    """Manage ClickUp lists."""
    pass


@list_group.command("list")
@click.option("--folder-id", default=None, help="Folder ID to list from.")
@click.option("--space-id", default=None, help="Space ID for folderless lists.")
def list_list(folder_id, space_id):
    """List lists in a folder or space."""
    client = get_client()

    if folder_id:
        lists = client.list_lists(folder_id)
    elif space_id:
        lists = client.list_folderless_lists(space_id)
    else:
        # Interactive: pick space, then folder
        workspace_id = get_workspace_id()
        spaces = client.list_spaces(workspace_id)
        if not spaces:
            console.print("[red]No spaces found.[/red]")
            raise SystemExit(1)
        for i, s in enumerate(spaces, 1):
            console.print(f"  {i}. {s.name}")
        choice = click.prompt("Select space", type=int, default=1)
        selected_space = spaces[choice - 1]

        folders = client.list_folders(selected_space.id)
        folderless = client.list_folderless_lists(selected_space.id)

        if folders:
            console.print("\nFolders:")
            for i, f in enumerate(folders, 1):
                console.print(f"  {i}. {f.name}")
            console.print(f"  {len(folders) + 1}. [Folderless lists]")
            fchoice = click.prompt("Select folder", type=int, default=1)

            if fchoice <= len(folders):
                lists = client.list_lists(folders[fchoice - 1].id)
            else:
                lists = folderless
        else:
            lists = folderless

    print_lists(lists)
```

**Step 2: Register in cli.py**

```python
from clickup_cli.commands.list import list_group
cli.add_command(list_group)
```

**Step 3: Commit**

```bash
git add src/clickup_cli/commands/list.py src/clickup_cli/cli.py
git commit -m "feat: add list command with interactive folder/space selection"
```

---

### Task 10: Task Commands

**Files:**
- Create: `src/clickup_cli/commands/task.py`
- Modify: `src/clickup_cli/cli.py`

**Step 1: Create task commands**

`src/clickup_cli/commands/task.py`:

```python
import click
from rich.console import Console

from clickup_cli.cli import get_client
from clickup_cli.formatting import print_task_detail, print_tasks

console = Console()


@click.group("task")
def task_group():
    """Manage ClickUp tasks."""
    pass


@task_group.command("list")
@click.option("--list-id", required=True, help="List ID to show tasks from.")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--assignee", default=None, help="Filter by assignee.")
def task_list(list_id, status, assignee):
    """List tasks in a ClickUp list."""
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
```

**Step 2: Register in cli.py**

```python
from clickup_cli.commands.task import task_group
cli.add_command(task_group)
```

**Step 3: Verify**

```bash
uv run clickup task --help
uv run clickup --help
```

**Step 4: Commit**

```bash
git add src/clickup_cli/commands/task.py src/clickup_cli/cli.py
git commit -m "feat: add task CRUD commands (list, view, create, update, delete)"
```

---

### Task 11: Add .gitignore and Final Cleanup

**Files:**
- Create: `.gitignore`

**Step 1: Create .gitignore**

`.gitignore`:

```
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/
.mypy_cache/
```

**Step 2: Final verification**

```bash
uv run clickup --help
uv run clickup config --help
uv run clickup space --help
uv run clickup folder --help
uv run clickup list --help
uv run clickup task --help
```

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```
