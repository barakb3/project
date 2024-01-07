import click

from . import read
from . import run_server
from . import run_webserver
from . import upload_thought


@click.group()
def group():
    pass


if __name__ == "__main__":
    group.add_command(read)
    group.add_command(run_server)
    group.add_command(run_webserver)
    group.add_command(upload_thought)
    group()
