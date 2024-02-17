import datetime as dt
import importlib
import inspect
from pathlib import Path

import click

import flask

from project_pb2 import ProtoSnapshot, ProtoUserInformation

from .constants import UINT32_SIZE_IN_BYTES
from .snapshot import Snapshot
from .user_information import UserInformation
from .utils import from_bytes


class Context:
    def __init__(self, user_id: int, data_dir_path: str, timestamp: int):
        self.user_id = user_id
        self.data_dir_path = data_dir_path
        self.datetime = dt.datetime.fromtimestamp(
            timestamp / 1000, tz=dt.timezone.utc  # Timestamp in milliseconds.
        )
        self.snapshot_dir_path = Path(
            self.data_dir_path,
            f"{self.user_id}",
            f"{self.datetime:%Y-%m-%d_%H-%M-%S-%f}",
        )

    def path(self, rel_path: str) -> Path:
        # `rel_path` is relative to the snapshot's directory path.
        path = self.snapshot_dir_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, file_rel_path: str, content: str):
        with open(self.path(rel_path=file_rel_path), "w") as f:
            f.write(content)


def load_parsers() -> dict:
    package_name = __package__.split(".")[-1]
    root_pkg_abs_path = Path.cwd() / package_name
    parsers_rel_path = Path("./parsers")

    parsers: dict = {}
    for path in Path(root_pkg_abs_path, parsers_rel_path).iterdir():
        if path.name.startswith("_") or not path.suffix == ".py":
            continue
        pkg_name = str(root_pkg_abs_path).split("/")[-1]
        rel_module_name = "." + ".".join(parsers_rel_path.parts)
        parser_module = importlib.import_module(
            f"{rel_module_name}.{path.stem}",
            package=pkg_name,
        )
        for key, value in parser_module.__dict__.items():
            if key.startswith("parse_") and inspect.isfunction(value):
                parsers[value.required_fields] = value
            elif key.endswith("Parser") and inspect.isclass(value):
                obj = value()
                parsers[obj.required_fields] = obj.parse

    return parsers


class Server:
    def __init__(self, host: str, port: int, data_dir_path: str):
        self.host = host
        self.port = port
        self.app = flask.Flask(__name__)

        self.data_dir_path = data_dir_path
        self.parsers = load_parsers()
        self.supported_fields = [
            parser for key in self.parsers.keys() for parser in key
        ]

        self.parsed_snapshots = 0

        @self.app.route("/config", methods=["GET"])
        def config():  # noqa: ANN201
            return self.supported_fields

        @self.app.route("/snapshot", methods=["POST"])
        def snapshot():  # noqa: ANN201
            response = flask.request
            user_information, snapshot = self.get_user_id_and_snapshot(
                data=response.get_data()
            )
            context = Context(
                user_id=user_information.id,
                data_dir_path=self.data_dir_path,
                timestamp=snapshot.timestamp
            )
            for required_fields, parser in self.parsers.items():
                args = [
                    snapshot[field] for field in required_fields
                    if field in self.supported_fields
                ]
                parser(context, *args)

            self.parsed_snapshots += 1
            print(f"Server processed {self.parsed_snapshots} snapshots.")
            return {"status": "success"}

    def get_user_id_and_snapshot(self, data: bytes) -> tuple:
        msg_index = 0
        user_information_size = from_bytes(
            data=data[0:UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES

        parsed_user_information = ProtoUserInformation()
        parsed_user_information.ParseFromString(
            data[msg_index:msg_index + user_information_size]
        )
        msg_index += user_information_size
        user_information = UserInformation.from_parsed(
            parsed=parsed_user_information
        )

        snapshot_size = from_bytes(
            data=data[msg_index:msg_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES

        parsed_snapshot = ProtoSnapshot()
        parsed_snapshot.ParseFromString(
            data[msg_index:msg_index + snapshot_size]
        )
        msg_index += snapshot_size

        assert (
            msg_index == len(data)
        ), "Message length received doesn't match."

        snapshot = Snapshot.from_parsed(parsed=parsed_snapshot)

        return (user_information, snapshot)

    def run(self):
        self.app.run(host=self.host, port=self.port)


@click.command()
@click.argument("address")
@click.argument("data_dir")
def run_server(address: str, data_dir: str):
    """
    Runs a server that serves some data directory.
    Can be stopped by `Ctrl+C`.

    :param address: A host and a port, e.g.: 127.0.0.1:5000.
    :type address: str
    :param data_dir: A path to the data directory the server will serve.
    :type data_dir: str ot Path-like objects

    """
    ip, port = address.split(":", 1)
    server = Server(host=ip, port=port, data_dir_path=data_dir)
    server.run()
