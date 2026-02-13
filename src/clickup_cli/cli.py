import click


@click.group()
@click.version_option()
def cli():
    """CLI tool for managing ClickUp tasks."""
    pass
