import datetime as dt

import click

from src.thought import Thought
from src.utils import Connection


@click.command()
@click.argument("address")
@click.argument("user_id")
@click.argument("thought")
def upload_thought(address: str, user_id: str, thought: str):
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
    t = Thought(user_id=user_id, timestamp=dt.datetime.now(), thought=thought)
    with Connection.connect(host=ip, port=int(port)) as connection:
        connection.send(t.serialize())
    print("done")
