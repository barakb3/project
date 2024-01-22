from typing import Callable, Union
from urllib.parse import urlparse

import click

from .drivers import BinaryDriver, ProtobufDriver


class Reader:
    """
    A class that reads a user sample containing thoughts.
    When initialized, it reads the user information and then functions as a
    snapshot generator.

    :param url: scheme://username:password@host:port/path?key=value#fragment
    :type address: str

    """
    def __init__(self, url: str) -> None:
        parsed_url = urlparse(url=url)
        self.driver: Union[BinaryDriver, ProtobufDriver] = find_driver(
            scheme=parsed_url.scheme
        )(parsed_url.path)
        self.user_information = self.driver.get_user_information()

        print(
            f"{self.user_information.id=}, "
            f"{self.user_information.username=}, "
            f"{self.user_information.birthday=}, "
            f"{self.user_information.gender=}."
        )

    def __iter__(self):
        while True:
            curr_snapshot = self.driver.get_snapshot()
            if curr_snapshot is None:
                break
            yield curr_snapshot

    @property
    def user_id(self) -> int:
        return self.user_information.id

    @property
    def username(self) -> str:
        return self.user_information.username


def find_driver(scheme: str) -> Callable:
    drivers = {
        "binary": BinaryDriver,
        "protobuf": ProtobufDriver,
    }
    for driver_scheme, cls in drivers.items():
        if scheme == driver_scheme:
            return cls
    else:
        raise Exception(f"Scheme '{scheme}' is not supported.")


@click.command()
@click.argument("path")
# TODO: Document this CLI function.
def read(path: str):
    reader = Reader(path)
    for i, snapshot in enumerate(reader):
        print(f"snapshot number: {i+1}, {snapshot.timestamp=}")
