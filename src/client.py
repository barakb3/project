import datetime as dt

import click

from src.constants import UINT32_SIZE_IN_BYTES
from src.protocol import Config, Hello, Snapshot
from src.reader import Reader
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


@click.command()
@click.argument("address")
@click.argument("sample_path")
def run(address: str, sample_path: str):
    ip, port = address.split(":", 1)
    reader = Reader(path=sample_path)

    hello_msg = Hello(
        user_id=reader.id,
        username=reader.name,
        birth_day=reader.birth_day,
        gender=reader.gender,
    )
    hello = hello_msg.serialize()

    for i, snapshot in enumerate(reader):
        snapshot: Snapshot
        with Connection.connect(host=ip, port=int(port)) as connection:
            connection: Connection
            connection.send_message(msg=hello)

            config_msg = connection.receive_message()
            if len(config_msg) < UINT32_SIZE_IN_BYTES:
                raise Exception("Incomplete meta data received.")
            config: Config = Config.deserialize(msg=config_msg)
            supported_fields = config.supported_fields

            snapshot_msg = snapshot.get_supported_fields_msg(
                supported_fields=supported_fields
            )

            connection.send_message(msg=snapshot_msg)
        print(f"Client sent {i + 1} snapshots.")
