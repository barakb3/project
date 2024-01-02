import datetime as dt
import click

from . import Thought
from .utils import Connection


@click.command()
@click.argument("address")
@click.argument("user_id")
@click.argument("thought")
def upload_thought(address, user_id, thought):
    """
    Upload some thought of some user to the server.

    :param address: A host and a port, e.g.: 127.0.0.1:5000.
    :type address: str
    :param user_id: The user Id, e.g. 2
    :type user_id: str
    :param thought: The thought the the user had.
    :type thought: str

    """
    ip, port = address.split(":", 1)
    t = Thought(user_id, dt.datetime.now(), thought)
    with Connection.connect(ip, int(port)) as connection:
        connection.send(t.serialize())
    print("done")
