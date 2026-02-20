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

    from clickup_cli.client import ClickUpClient

    client = ClickUpClient(api_token)
    user = client.get_user()
    if not user:
        console.print("[red]Could not fetch user info. Check your API token.[/red]")
        raise SystemExit(1)
    console.print(f"Authenticated as: [bold]{user.get('username', user.get('email', 'unknown'))}[/bold]")
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
        "user_id": user["id"],
        "username": user.get("username", user.get("email", "")),
        "workspace_id": workspace["id"],
        "workspace_name": workspace["name"],
    }
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
