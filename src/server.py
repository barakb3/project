import datetime as dt
import importlib
import inspect
import threading
from pathlib import Path

import click

from .constants import (
    DOUBLE_SIZE_IN_BYTES,
    FLOAT_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from .protocol import (
    Config,
    Hello,
    NUM_BYTES_PIXEL_COLOR_IMAGE,
)
from .utils import Connection, Listener, from_bytes

NUM_BYTES_TRANSLATION = 3 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_ROTATION = 4 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_PIXEL_DEPTH_IMAGE = FLOAT_SIZE_IN_BYTES
NUM_BYTES_FEELINGS = 4 * FLOAT_SIZE_IN_BYTES


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
        self.snapshot_dir_path.mkdir(parents=True, exist_ok=True)

    def path(self, file_rel_path: str) -> Path:
        return self.snapshot_dir_path / file_rel_path

    def save(self, file_rel_path: str, content: str):
        # `file_rel_path` is relative to the snapshot's directory path.
        with open(self.path(file_rel_path=file_rel_path), "w") as f:
            f.write(content)


class Handler(threading.Thread):
    def __init__(
            self,
            client: Connection,
            data_dir: str,
            lock: threading.Lock,
            parsers: dict,
            thread_number: int,
    ):
        super().__init__()
        self.client = client
        self.data_dir_path = Path(data_dir)
        self.lock = lock
        self.parsers = parsers
        self.thread_number = thread_number

    def run(self):
        hello_msg = self.client.receive_message()
        if len(hello_msg) < UINT32_SIZE_IN_BYTES:
            raise Exception("Incomplete meta data received.")
        user_id = Hello.deserialize(msg=hello_msg).user_id

        supported_fields = tuple(
            parser for key in self.parsers.keys() for parser in key
        )
        config = Config(supported_fields=supported_fields)
        self.client.send_message(msg=config.serialize())

        snapshot_msg = self.client.receive_message()
        if len(snapshot_msg) < UINT32_SIZE_IN_BYTES:
            raise Exception("Incomplete meta data received.")

        self.lock.acquire()
        self.process_snapshot(snapshot_msg=snapshot_msg, user_id=user_id)
        self.lock.release()

        self.client.close()
        print(f"Server processed {self.thread_number} snapshots.")

    def process_snapshot(self, snapshot_msg: bytes, user_id: int):
        msg_index = 0
        timestamp = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT64_SIZE_IN_BYTES],
            data_type="uint64",
            endianness="<",
        )
        msg_index += UINT64_SIZE_IN_BYTES

        preprocessed_data = {}

        preprocessed_data["translation"] = snapshot_msg[
            msg_index:msg_index + NUM_BYTES_TRANSLATION
        ]
        msg_index += NUM_BYTES_TRANSLATION

        preprocessed_data["rotation"] = snapshot_msg[
            msg_index:msg_index + NUM_BYTES_ROTATION
        ]
        msg_index += NUM_BYTES_ROTATION

        start_color_image = msg_index
        color_image_width = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        color_image_height = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        # Add image bytes.
        msg_index += (
            NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
        )
        end_color_image = msg_index
        preprocessed_data["color_image"] = snapshot_msg[
            start_color_image:end_color_image
        ]

        start_depth_image = msg_index
        depth_image_width = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        depth_image_height = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        # Add image bytes.
        msg_index += (
            NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height  # noqa: E501
        )
        end_depth_image = msg_index
        preprocessed_data["depth_image"] = snapshot_msg[
            start_depth_image:end_depth_image
        ]

        preprocessed_data["feelings"] = snapshot_msg[
            msg_index:msg_index + NUM_BYTES_FEELINGS
        ]
        msg_index += NUM_BYTES_FEELINGS

        context = Context(
            user_id=user_id,
            data_dir_path=self.data_dir_path,
            timestamp=timestamp
        )
        for required_fields, parser in self.parsers.items():
            args = [
                arg for field, arg in preprocessed_data.items()
                if field in required_fields
            ]
            parser(context, *args)

        assert (
            msg_index == len(snapshot_msg)
        ), "Message length received doesn't match."


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
    with Listener(port=int(port), host=ip) as listener:
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

        lock = threading.Lock()

        thread_number = 1
        while True:
            client = listener.accept()
            newthread = Handler(
                client=client,
                data_dir=data_dir,
                lock=lock,
                parsers=parsers,
                thread_number=thread_number,
            )
            newthread.start()
            thread_number += 1
