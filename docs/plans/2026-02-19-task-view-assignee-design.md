# Design: task view — assignee list mode

Date: 2026-02-19

## Summary

Extend `cl task view` to support listing all open tasks assigned to a user. When called with no `task_id`, it defaults to showing the current authenticated user's open tasks. A `--user` option allows querying another user by ID.

## Command Shape

```
cl task view                  # list my open tasks (default)
cl task view TASK_ID          # single task detail (existing, unchanged)
cl task view --user 12345     # list another user's open tasks
```

`--me` flag is intentionally omitted — no args already implies current user.

## Behaviour Rules

- `task_id` present → single-task mode; `--user` is ignored.
- `task_id` absent + `--user` given → list mode for specified user.
- `task_id` absent + no `--user` → list mode for current authenticated user.
- List mode defaults to open tasks only (`include_closed=false`).

## Implementation

### `commands/task.py`

- Make `task_id` an optional argument (`required=False, default=None`).
- Add `--user` / `-u` option (`user_id`, default `None`).
- Branch on `task_id`:
  - Present → existing `client.get_task()` + `print_task_detail()` path.
  - Absent → resolve user ID (read `config["user_id"]` if `--user` not given), call new `client.get_workspace_tasks()`, render with `print_tasks()`.

### `client.py`

Add new method:

```python
def get_workspace_tasks(self, team_id: str, assignee_id: int) -> list[Task]:
    params = {"assignees[]": [assignee_id], "include_closed": "false"}
    data = self._request("GET", f"/team/{team_id}/task", params=params)
    return [Task.from_api(t) for t in data.get("tasks", [])]
```

### Helpers used

- `get_workspace_id()` — already exists in `helpers.py`, provides `team_id`.
- `load_config()["user_id"]` — `user_id` is persisted to config during `cl config init`, no API call needed.

### Skill maintenance

Update `~/.claude/skills/clickup-task-management/SKILL.md` to reflect the new `task view` signature.
