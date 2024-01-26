import datetime as dt
import importlib
import inspect
from pathlib import Path

import click

import flask

from project_pb2 import ProtoSnapshot, ProtoUserInformation

from .constants import UINT32_SIZE_IN_BYTES
from .snapshot import Snapshot
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
    parsers = load_parsers()
    supported_fields = [
        parser for key in parsers.keys() for parser in key
    ]

    app = flask.Flask(__name__)

    @app.route("/config", methods=["GET"])
    def send_config():  # noqa: ANN201
        try:
            return supported_fields
        except Exception as err:
            return flask.jsonify(
                {"status": 1, "error": str(err)}
            )

    @app.route("/snapshot", methods=["POST"])
    def process_snapshot():  # noqa: ANN201
        try:
            response = flask.request
            data = response.get_data()

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

            context = Context(
                user_id=parsed_user_information.user_id,
                data_dir_path=data_dir,
                timestamp=parsed_snapshot.datetime
            )
            for required_fields, parser in parsers.items():
                args = [
                    snapshot[field] for field in required_fields
                    if field in supported_fields
                ]
                parser(context, *args)

            print("Server processed another snapshots.")
            return {"status": "success"}
        except Exception as err:
            return {"status_code": "failure", "error": str(err)}

    ip, port = address.split(":", 1)
    app.run(host=ip, port=port)
