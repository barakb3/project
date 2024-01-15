import io

import click

from ..constants import (
    CHAR_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from ..protocol import Snapshot, from_bytes


class Reader:
    # TODO: Document this class.
    def __init__(self, path: str) -> None:
        self.file: io.BufferedReader = open(path, "rb")
        self.id: int
        self.name: str
        self.birth_day: int
        self.gender: str
        self.read_sample_metadata()

        print(f"{self.id=}, {self.name=}, {self.birth_day=}, {self.gender=}")

    def __iter__(self):
        while True:
            curr_snapshot = Snapshot.read_from_file(file=self.file)
            if curr_snapshot is None:
                break
            yield curr_snapshot

    @property
    def user_id(self) -> int:
        return self.id

    @property
    def username(self) -> str:
        return self.name

    def read_sample_metadata(self):
        self.id: int = from_bytes(
            data=self.file.read(UINT64_SIZE_IN_BYTES),
            data_type="uint64",
            endianness="<",
        )
        name_length: int = from_bytes(
            data=self.file.read(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        self.name: str = from_bytes(
            data=self.file.read(name_length),
            data_type="string",
            endianness="<",
        )
        self.birth_day: int = from_bytes(
            data=self.file.read(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        self.gender: str = from_bytes(
            data=self.file.read(CHAR_SIZE_IN_BYTES),
            data_type="char",
            endianness="<",
        )


@click.command()
@click.argument("path")
def read(path: str):
    # TODO: Document this CLI function.
    reader = Reader(path)
    i = 0
    for i, snapshot in enumerate(reader):
        print(f"snapshot number: {i+1}")
