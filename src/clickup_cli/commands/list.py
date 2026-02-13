import click
from rich.console import Console

from clickup_cli.helpers import get_client, get_workspace_id
from clickup_cli.formatting import print_lists

console = Console()


@click.group("list")
def list_group():
    """Manage ClickUp lists."""
    pass


@list_group.command("list")
@click.option("--folder-id", default=None, help="Folder ID to list from.")
@click.option("--space-id", default=None, help="Space ID for folderless lists.")
def list_list(folder_id, space_id):
    """List lists in a folder or space."""
    client = get_client()

    if folder_id:
        lists = client.list_lists(folder_id)
    elif space_id:
        lists = client.list_folderless_lists(space_id)
    else:
        workspace_id = get_workspace_id()
        spaces = client.list_spaces(workspace_id)
        if not spaces:
            console.print("[red]No spaces found.[/red]")
            raise SystemExit(1)
        for i, s in enumerate(spaces, 1):
            console.print(f"  {i}. {s.name}")
        choice = click.prompt("Select space", type=int, default=1)
        selected_space = spaces[choice - 1]

        folders = client.list_folders(selected_space.id)
        folderless = client.list_folderless_lists(selected_space.id)

        if folders:
            console.print("\nFolders:")
            for i, f in enumerate(folders, 1):
                console.print(f"  {i}. {f.name}")
            console.print(f"  {len(folders) + 1}. [Folderless lists]")
            fchoice = click.prompt("Select folder", type=int, default=1)

            if fchoice <= len(folders):
                lists = client.list_lists(folders[fchoice - 1].id)
            else:
                lists = folderless
        else:
            lists = folderless

    print_lists(lists)
