import click

from clickup_cli.commands.config_cmd import config_group
from clickup_cli.commands.folder import folder_group
from clickup_cli.commands.list import list_group
from clickup_cli.commands.space import space_group


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """CLI tool for managing ClickUp tasks."""
    ctx.ensure_object(dict)


cli.add_command(config_group)
cli.add_command(space_group)
cli.add_command(folder_group)
cli.add_command(list_group)
