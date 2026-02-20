# task view Assignee List Mode Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend `cl task view` to list open tasks assigned to a user when called without a task ID.

**Architecture:** Make `task_id` optional on `task view`; add `--user` option; add `get_workspace_tasks()` to `ClickUpClient` that hits `/team/{team_id}/task` filtered by assignee with `include_closed=false`. When no `task_id` and no `--user` is given, read `user_id` from config (already stored during `cl config init`).

**Tech Stack:** Python, Click, httpx, Rich

---

### Task 1: Add `get_workspace_tasks()` to ClickUpClient

**Files:**
- Modify: `src/clickup_cli/client.py` (after line 80, the `get_task` method)

> Note: No tests are configured in this project yet — skip test steps.

**Step 1: Add the method**

In `src/clickup_cli/client.py`, insert after the `get_task` method (after line 80):

```python
def get_workspace_tasks(self, team_id: str, assignee_id: int) -> list[Task]:
    params = {"assignees[]": [assignee_id], "include_closed": "false"}
    data = self._request("GET", f"/team/{team_id}/task", params=params)
    return [Task.from_api(t) for t in data.get("tasks", [])]
```

**Step 2: Commit**

```bash
git add src/clickup_cli/client.py
git commit -m "feat: add get_workspace_tasks() to ClickUpClient"
```

---

### Task 2: Update `task view` command

**Files:**
- Modify: `src/clickup_cli/commands/task.py` (lines 45–51, the `task_view` function)

**Step 1: Add missing imports at the top of the file**

The file currently imports:
```python
from clickup_cli.helpers import get_client, resolve_alias
```

Change it to:
```python
from clickup_cli.helpers import get_client, get_workspace_id, resolve_alias
from clickup_cli.config import load_config
```

**Step 2: Replace the `task_view` function**

Replace the current `task_view` function (lines 45–51):

```python
@task_group.command("view")
@click.argument("task_id")
def task_view(task_id):
    """View a single task's details."""
    client = get_client()
    task = client.get_task(task_id)
    print_task_detail(task)
```

With:

```python
@task_group.command("view")
@click.argument("task_id", required=False, default=None)
@click.option("-u", "--user", "user_id", default=None, help="User ID to filter by (default: current user).")
def task_view(task_id, user_id):
    """View a task by ID, or list open tasks assigned to a user."""
    client = get_client()
    if task_id:
        task = client.get_task(task_id)
        print_task_detail(task)
    else:
        if user_id is None:
            config = load_config()
            user_id = config["user_id"]
        workspace_id = get_workspace_id()
        tasks = client.get_workspace_tasks(workspace_id, user_id)
        print_tasks(tasks)
```

**Step 3: Smoke test**

```bash
uv run cl task view
# Expected: Rich table of your open tasks

uv run cl task view --user <some_user_id>
# Expected: Rich table of that user's open tasks

uv run cl task view <task_id>
# Expected: single task detail block (unchanged behaviour)
```

**Step 4: Commit**

```bash
git add src/clickup_cli/commands/task.py
git commit -m "feat: task view defaults to listing current user's open tasks"
```

---

### Task 3: Update skill SKILL.md

**Files:**
- Modify: `~/.claude/skills/clickup-task-management/SKILL.md`

**Step 1: Update the Quick Reference table**

Replace:
```markdown
| View task | `cl task view TASK_ID` |
```

With:
```markdown
| View task | `cl task view TASK_ID` |
| My open tasks | `cl task view` |
| User's open tasks | `cl task view -u USER_ID` |
```

**Step 2: Add an example to the Examples section**

Add after the `# Filter tasks` example:

```bash
# View my open tasks (across workspace)
cl task view

# View another user's open tasks
cl task view -u 12345678
```

**Step 3: Commit**

```bash
git add ~/.claude/skills/clickup-task-management/SKILL.md
git commit -m "docs: update skill with task view assignee list mode"
```
