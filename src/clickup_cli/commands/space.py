import click

from clickup_cli.helpers import get_client, get_workspace_id
from clickup_cli.formatting import print_spaces


@click.group("space")
def space_group():
    """Manage ClickUp spaces."""
    pass


@space_group.command("list")
def space_list():
    """List all spaces in the workspace."""
    client = get_client()
    workspace_id = get_workspace_id()
    spaces = client.list_spaces(workspace_id)
    print_spaces(spaces)
