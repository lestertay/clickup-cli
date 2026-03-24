# Enable Unassigning Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `-r/--remove-assignee` flag to `cl task update` that removes a user from a task's assignees via the ClickUp API.

**Architecture:** The ClickUp API v2 `PUT /task/{task_id}` accepts `assignees.add` and `assignees.rem` arrays. Currently only `add` is used. This plan adds a `--remove-assignee` option that populates `rem`. Both `-a` (add) and `-r` (remove) can be used in the same command.

**Tech Stack:** Click (CLI options), httpx (already handles the PUT request), ClickUp API v2.

---

### Task 1: Add `--remove-assignee` flag to `task update`

**Files:**
- Modify: `src/clickup_cli/commands/task.py:101-140`

**Context:** The `assignees` field in the update payload is a dict with `add` and/or `rem` keys, each an array of integer user IDs. Currently the code only ever sets `add`. We need to also support `rem`.

ClickUp API payload shape:
```json
{
  "assignees": {
    "add": [12345],
    "rem": [67890]
  }
}
```

**Step 1: Add the `-r/--remove-assignee` option**

In `src/clickup_cli/commands/task.py`, add a new option to `task_update` after the existing `-a/--assignee` option:

```python
@click.option("-r", "--remove-assignee", default=None, help="Assignee user ID to remove.")
```

Also update the function signature from:
```python
def task_update(task_id, name, description, status, priority, assignee, due_date, tag, time_estimate):
```
to:
```python
def task_update(task_id, name, description, status, priority, assignee, remove_assignee, due_date, tag, time_estimate):
```

**Step 2: Build the `assignees` payload combining add and rem**

Replace the current assignee block:
```python
if assignee:
    task_data["assignees"] = {"add": [int(assignee)]}
```

With:
```python
assignees_payload = {}
if assignee:
    assignees_payload["add"] = [int(assignee)]
if remove_assignee:
    assignees_payload["rem"] = [int(remove_assignee)]
if assignees_payload:
    task_data["assignees"] = assignees_payload
```

**Step 3: Manual smoke test — remove an assignee**

First, assign yourself to a test task, then remove yourself:

```bash
# Add yourself as assignee (use your actual user ID from `cl config show`)
uv run cl task update 86ewp18jv -a YOUR_USER_ID

# View task to confirm assignee was added
uv run cl task view 86ewp18jv

# Now remove yourself
uv run cl task update 86ewp18jv -r YOUR_USER_ID

# View task to confirm assignee was removed
uv run cl task view 86ewp18jv
```

Expected: after remove, "Assignees: -" (or the user is gone from the list).

**Step 4: Manual smoke test — add and remove simultaneously**

If two users are available, confirm both flags work together:
```bash
uv run cl task update TASK_ID -a USER_A -r USER_B
```

Expected: API call succeeds, USER_A added, USER_B removed.

**Step 5: Commit**

```bash
git add src/clickup_cli/commands/task.py
git commit -m "feat: add --remove-assignee flag to task update"
```

---

### Task 2: Update the skill file

**Files:**
- Modify: `~/.claude/skills/clickup-task-management/SKILL.md`

**Step 1: Add `-r` row to the Task Options table**

In the Task Options table, after the `-a` row:
```markdown
| `-r` | `--remove-assignee` | User ID to remove |
```

**Step 2: Add an example under the Examples section**

After the "Update status and estimate" example:
```bash
# Remove an assignee
cl task update abc123 -r 12345678
```

**Step 3: Commit**

```bash
git add ~/.claude/skills/clickup-task-management/SKILL.md
git commit -m "docs: update skill with --remove-assignee flag"
```
