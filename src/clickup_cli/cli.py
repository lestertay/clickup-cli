import click

from clickup_cli.commands.config_cmd import config_group


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    """CLI tool for managing ClickUp tasks."""
    ctx.ensure_object(dict)


cli.add_command(config_group)
