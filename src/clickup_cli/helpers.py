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
