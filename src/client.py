import click

import requests

from .reader import Reader
from .snapshot import Snapshot


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

    for i, snapshot in enumerate(reader):
        snapshot: Snapshot
        response_config = requests.get(f"http://{ip}:{port}/config")
        supported_fields = tuple(response_config.json())

        supported_snapshot = snapshot.clone_by_supported_fields(
            supported_fields=supported_fields
        )
        user_information_to_send = reader.user_information.serialize()
        snapshot_to_send = supported_snapshot.serialize()
        data = b"".join(user_information_to_send, snapshot_to_send)
        headers = {
            "Content-Type": "application/octet-stream"
        }
        response_snapshot = requests.post(
            f"http://{ip}:{port}/snapshot", data=data, headers=headers
        )
        print(
            f"Client sent {i + 1} snapshots.\n"
            f"Server response is {response_snapshot.text}"
        )
