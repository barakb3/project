import click

from src.client import run
from src.reader import read
from src.server import run_server
from src.web import run_webserver


@click.group()
def server():
    pass


@click.group()
def client():
    pass


client.add_command(read)
client.add_command(run)
server.add_command(run_server)
server.add_command(run_webserver)

__all__ = [
    "client",  # CLI.
    "run_server",
    "run_webserver",
    "server",  # CLI.
]
