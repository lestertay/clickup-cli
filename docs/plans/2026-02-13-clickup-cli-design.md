# ClickUp CLI — Design Document

## Purpose

A Python CLI tool for day-to-day task management in ClickUp. Create, update, view, and organize tasks without leaving the terminal.

## Decisions

- **Framework**: Click (flat command structure)
- **Package management**: uv
- **Version control**: git
- **HTTP client**: httpx
- **Output**: Rich terminal tables
- **Config**: `~/.clickup-cli/config.yaml`
- **Scope**: Single workspace

## Project Structure

```
clickup-cli/
├── pyproject.toml
├── src/
│   └── clickup_cli/
│       ├── __init__.py
│       ├── cli.py              # Click entry point + command group registration
│       ├── config.py           # Config file loading/saving
│       ├── client.py           # ClickUp API v2 HTTP client
│       ├── models.py           # Dataclasses for Space, Folder, List, Task
│       ├── formatting.py       # Rich table output
│       └── commands/
│           ├── __init__.py
│           ├── space.py        # space list
│           ├── folder.py       # folder list
│           ├── list.py         # list list
│           ├── task.py         # task list, create, update, delete, view
│           └── config_cmd.py   # config init, config show
```

## Dependencies

- `click` — CLI framework
- `httpx` — HTTP client
- `rich` — Terminal tables and formatting
- `pyyaml` — Config file parsing

## Config File

Location: `~/.clickup-cli/config.yaml`

```yaml
api_token: "pk_..."
workspace_id: "12345"
```

## Command Interface

All commands follow `clickup <resource> <action> [args] [options]`.

### Config

```
clickup config init          # Interactive setup
clickup config show          # Display current config
```

### Hierarchy Browsing

```
clickup space list
clickup folder list --space-id ID
clickup list list --folder-id ID
```

### Tasks

```
clickup task list --list-id ID [--status STATUS] [--assignee NAME] [--priority LEVEL]
clickup task view TASK_ID
clickup task create --list-id ID --name "..." [--description "..."] [--status S] [--priority P] [--assignee A] [--due-date YYYY-MM-DD] [--tag TAG]
clickup task update TASK_ID [--name "..."] [--status S] [--priority P] [--assignee A] [--due-date YYYY-MM-DD] [--tag TAG]
clickup task delete TASK_ID
```

When `--list-id`, `--space-id`, or `--folder-id` is omitted, the CLI prompts with interactive selection.

## Architecture

### Layers

1. **CLI** (`cli.py` + `commands/`) — Click groups, arg parsing, calls client, passes to formatting
2. **Client** (`client.py`) — ClickUp API v2 wrapper. Auth headers, base URL, error handling. Returns parsed dataclasses.
3. **Models** (`models.py`) — Dataclasses: `Space`, `Folder`, `TaskList`, `Task`
4. **Formatting** (`formatting.py`) — Rich table rendering
5. **Config** (`config.py`) — Load/save YAML config

### Data Flow

```
User runs command → Click parses args → Load config → Client HTTP request → Parse into model → Rich table output
```

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get workspaces | GET | `/team` |
| List spaces | GET | `/team/{team_id}/space` |
| List folders | GET | `/space/{space_id}/folder` |
| List lists (in folder) | GET | `/folder/{folder_id}/list` |
| List folderless lists | GET | `/space/{space_id}/list` |
| Get task | GET | `/task/{task_id}` |
| List tasks | GET | `/list/{list_id}/task` |
| Create task | POST | `/list/{list_id}/task` |
| Update task | PUT | `/task/{task_id}` |
| Delete task | DELETE | `/task/{task_id}` |

Base URL: `https://api.clickup.com/api/v2`
Auth: `Authorization: {api_token}` header

## Error Handling

- Invalid/missing config → clear message with `clickup config init` hint
- API errors (401, 404, 429) → human-readable messages, no tracebacks
- Network errors → "Could not reach ClickUp API" message

## Task Fields

name, status, assignee, due date, priority, tags
