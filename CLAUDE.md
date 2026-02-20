# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync              # Install dependencies
uv run cl       # Run the CLI
```

No tests or linter are configured yet.

## Architecture

This is a CLI tool for managing ClickUp resources (spaces, folders, lists, tasks) via the ClickUp API v2. Built with Click (command groups), Rich (table output), and httpx (HTTP client).

**Entrypoint:** `src/clickup_cli/cli.py` — registers Click command groups (`alias`, `config`, `space`, `folder`, `list`, `task`).

**Key layers:**
- `commands/` — Click command groups. Each file defines a `@click.group` with subcommands. Commands receive user input, resolve aliases, then delegate to the client.
- `client.py` — `ClickUpClient` wraps all ClickUp API v2 calls. Uses httpx with auth header. Returns model dataclasses.
- `models.py` — Dataclasses (`Space`, `Folder`, `TaskList`, `Task`) with `from_api()` classmethods that parse API JSON responses.
- `formatting.py` — Rich table rendering for each model type. Converts Unix timestamps (ms) to local time.
- `helpers.py` — `get_client()`, `get_workspace_id()`, and `resolve_alias()`. The alias system resolves `@name` references to resource IDs using the config file.
- `config.py` — Reads/writes `~/.clickup-cli/config.yaml`. Aliases are stored under the `aliases` key as `name: "type:id"`.

**Alias system:** Users can set named aliases (`cl alias set dev --space-id 12345`) that are stored in config.yaml. Any command option that takes a resource ID accepts `@alias` syntax, resolved via `resolve_alias(value, expected_type)` in each command function.

**Adding a new command group:** Create a file in `commands/`, define a `@click.group`, import and register it in `cli.py` with `cli.add_command()`.

**Adding a new API resource:** Add a dataclass with `from_api()` in `models.py`, add client methods in `client.py`, add a print function in `formatting.py`, then create the command group.

## Skill Maintenance

Whenever CLI commands are added, removed, or changed, update the corresponding skill file at `~/.claude/skills/clickup-task-management/SKILL.md` to keep the Quick Reference table and examples in sync.
