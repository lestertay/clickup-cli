import click

from clickup_cli.commands.config_cmd import config_group


@click.group()
@click.version_option()
def cli():
    """CLI tool for managing ClickUp tasks."""
    pass


cli.add_command(config_group)
