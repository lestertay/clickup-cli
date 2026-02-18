from rich.console import Console

from clickup_cli.client import ClickUpClient
from clickup_cli.config import load_config

console = Console()


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


def resolve_alias(value: str, expected_type: str | None = None) -> str:
    """Resolve @alias to ID. Pass through raw IDs unchanged."""
    if not value.startswith("@"):
        return value
    alias_name = value[1:]
    config = load_config()
    aliases = config.get("aliases", {})
    if alias_name not in aliases:
        console.print(f"[red]Alias '{alias_name}' not found. Run 'clickup alias list'.[/red]")
        raise SystemExit(1)
    stored = aliases[alias_name]  # e.g. "space:12345"
    alias_type, alias_id = stored.split(":", 1)
    if expected_type and alias_type != expected_type:
        console.print(f"[red]Alias '{alias_name}' is a {alias_type}, but a {expected_type} ID is expected.[/red]")
        raise SystemExit(1)
    return alias_id
