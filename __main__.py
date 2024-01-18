import click

from .src import client, server


@click.group()
def group():
    pass


if __name__ == "__main__":
    group.add_command(client)
    group.add_command(server)
    group()
