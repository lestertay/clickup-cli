import click
from rich.console import Console
from rich.table import Table

from clickup_cli.config import load_config, save_config

console = Console()


@click.group("alias")
def alias_group():
    """Manage named aliases for ClickUp resource IDs."""
    pass


@alias_group.command("set")
@click.argument("name")
@click.option("-s", "--space-id", default=None, help="Space ID to alias.")
@click.option("-f", "--folder-id", default=None, help="Folder ID to alias.")
@click.option("-l", "--list-id", default=None, help="List ID to alias.")
def alias_set(name, space_id, folder_id, list_id):
    """Set an alias for a resource ID."""
    provided = [(k, v) for k, v in [("space", space_id), ("folder", folder_id), ("list", list_id)] if v]
    if len(provided) != 1:
        console.print("[red]Provide exactly one of --space-id, --folder-id, or --list-id.[/red]")
        raise SystemExit(1)
    resource_type, resource_id = provided[0]
    config = load_config()
    aliases = config.setdefault("aliases", {})
    aliases[name] = f"{resource_type}:{resource_id}"
    save_config(config)
    console.print(f"[green]Alias '@{name}' set to {resource_type} {resource_id}.[/green]")


@alias_group.command("list")
def alias_list():
    """List all aliases."""
    config = load_config()
    aliases = config.get("aliases", {})
    if not aliases:
        console.print("[yellow]No aliases defined. Use 'cl alias set' to create one.[/yellow]")
        return
    table = Table(title="Aliases")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("ID", style="white")
    for name, value in sorted(aliases.items()):
        alias_type, alias_id = value.split(":", 1)
        table.add_row(f"@{name}", alias_type, alias_id)
    console.print(table)


@alias_group.command("remove")
@click.argument("name")
def alias_remove(name):
    """Remove an alias."""
    config = load_config()
    aliases = config.get("aliases", {})
    if name not in aliases:
        console.print(f"[red]Alias '{name}' not found.[/red]")
        raise SystemExit(1)
    del aliases[name]
    save_config(config)
    console.print(f"[green]Alias '@{name}' removed.[/green]")
