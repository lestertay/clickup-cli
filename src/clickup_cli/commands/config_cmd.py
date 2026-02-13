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
