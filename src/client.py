import click

from .constants import UINT32_SIZE_IN_BYTES
from .protocol import Config, Hello, Snapshot
from .reader import Reader
from .utils import Connection


@click.command()
@click.argument("address")
@click.argument("url")
def run(address: str, url: str):
    """
    Upload some snapshots from a file to the server.

    :param address: A host and a port, e.g.: 127.0.0.1:5000.
    :type address: str
    :param url: scheme://username:password@host:port/path?key=value#fragment.
    :type url: str

    """
    ip, port = address.split(":", 1)
    reader = Reader(url=url)

    hello_msg = Hello(
        user_id=reader.user_information.id,
        username=reader.user_information.username,
        birthday=reader.user_information.birthday,
        gender=reader.user_information.gender,
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
