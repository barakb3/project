import datetime as dt
import click

from . import Thought
from .utils import Connection


@click.command()
@click.argument("address")
@click.argument("user_id")
@click.argument("thought")
def upload_thought(address, user_id, thought):
    ip, port = address.split(":", 1)
    t = Thought(user_id, dt.datetime.now(), thought)
    with Connection.connect(ip, int(port)) as connection:
        connection.send(t.serialize())
    print("done")
