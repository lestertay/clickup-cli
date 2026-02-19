import click
from rich.console import Console

from clickup_cli.helpers import get_client, get_workspace_id, resolve_alias
from clickup_cli.formatting import print_folders

console = Console()


@click.group("folder")
def folder_group():
    """Manage ClickUp folders."""
    pass


@folder_group.command("list")
@click.option("-s", "--space-id", default=None, help="Space ID to list folders from.")
def folder_list(space_id):
    """List folders in a space."""
    if space_id:
        space_id = resolve_alias(space_id, "space")
    client = get_client()

    if not space_id:
        workspace_id = get_workspace_id()
        spaces = client.list_spaces(workspace_id)
        if not spaces:
            console.print("[red]No spaces found.[/red]")
            raise SystemExit(1)
        for i, s in enumerate(spaces, 1):
            console.print(f"  {i}. {s.name} ({s.id})")
        choice = click.prompt("Select space", type=int, default=1)
        space_id = spaces[choice - 1].id

    folders = client.list_folders(space_id)
    print_folders(folders)
