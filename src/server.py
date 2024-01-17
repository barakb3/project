import datetime as dt
import functools
import json
import threading
from pathlib import Path
from typing import Callable

from PIL import Image

import click

from .constants import (
    BYTE_SIZE_IN_BYTES,
    DOUBLE_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from .protocol import (
    Config,
    Hello,
    NUM_BYTES_FEELINGS,
    NUM_BYTES_PIXEL_COLOR_IMAGE,
    NUM_BYTES_PIXEL_DEPTH_IMAGE,
    NUM_BYTES_ROTATION,
    NUM_BYTES_TRANSLATION,
    Snapshot,
    from_bytes,
)
from .thought import Thought
from .utils import Connection, Listener


class Parser:
    def __init__(self):
        self.parsers: dict = {}

    def add_parser(self, name: str) -> Callable:
        def decorator(f: Callable) -> Callable:
            @functools.wraps(f)
            def wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN201
                return f(*args, **kwargs)
            self.parsers[name] = f
            return wrapper
        return decorator


class Handler(threading.Thread):
    def __init__(
            self,
            client: Connection,
            data_dir: str,
            lock: threading.Lock,
            parser: Parser,
            thread_number: int,
    ):
        super().__init__()
        self.client = client
        self.data_dir_path = Path(data_dir)
        self.lock = lock
        self.msg: bytearray = None
        self.thought: Thought = None
        self.parser = parser
        self.thread_number = thread_number

    def deprecated_run(self):
        msg = self.read_message()
        if len(msg) < 20:
            raise Exception("Incomplete meta data received.")
        self.thought = Thought.deserialize(data=msg)
        self.lock.acquire()
        self.write_thought()
        self.lock.release()
        self.client.close()

    def run(self):
        hello_msg = self.client.receive_message()
        if len(hello_msg) < UINT32_SIZE_IN_BYTES:
            raise Exception("Incomplete meta data received.")
        user_id = Hello.deserialize(msg=hello_msg).user_id

        config = Config(supported_fields=tuple(self.parser.parsers.keys()))
        self.client.send_message(msg=config.serialize())

        snapshot_msg = self.client.receive_message()
        if len(snapshot_msg) < UINT32_SIZE_IN_BYTES:
            raise Exception("Incomplete meta data received.")

        self.lock.acquire()
        self.process_snapshot(snapshot_msg=snapshot_msg, user_id=user_id)
        self.lock.release()

        self.client.close()
        print(f"Server processed {self.thread_number} snapshots.")

    def read_message(self) -> bytearray:
        msg = bytearray(self.client.receive(1024))
        while (cont_msg := self.client.receive(1024)):
            msg += cont_msg
        return msg

    def validate_message(self):
        if len(self.msg) < 20:
            raise Exception("Incomplete meta data received.")

    def process_snapshot(self, snapshot_msg: bytes, user_id: int):
        msg_index = 0
        timestamp = from_bytes(
            data=snapshot_msg[msg_index:msg_index + UINT64_SIZE_IN_BYTES],
            data_type="uint64",
            endianness="<",
        )
        msg_index += UINT64_SIZE_IN_BYTES

        datetime = dt.datetime.fromtimestamp(
            timestamp / 1000, tz=dt.timezone.utc  # Timestamp in milliseconds.
        )
        snapshot_dir_path = self.data_dir_path / \
            f"{user_id}" / \
            f"{datetime:%Y-%m-%d_%H-%M-%S-%f}"
        snapshot_dir_path.mkdir(parents=True, exist_ok=True)

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

        for field_name, parser in self.parser.parsers.items():
            parser(snapshot_dir_path, preprocessed_data[field_name])

        assert (
            msg_index == len(snapshot_msg)
        ), "Message length received doesn't match."

    def write_thought(self):
        dir_path = self.data_dir_path / f"{self.thought.user_id}"
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = \
            dir_path / f"{self.thought.timestamp:%Y-%m-%d_%H-%M-%S}.txt"
        file_path.touch()
        with file_path.open(mode="r+") as f:
            if f.read() == "":
                f.write(f"{self.thought.thought}")
            else:
                f.write(f"\n{self.thought.thought}")


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
        parser = Parser()

        @parser.add_parser("translation")
        def parse_translation(snapshot_dir_path: Path, translation_msg: bytes):
            translation = []
            msg_index = 0
            for _ in range(3):
                translation.append(
                    from_bytes(
                        data=translation_msg[
                            msg_index:msg_index + DOUBLE_SIZE_IN_BYTES
                        ],
                        data_type="double",
                        endianness="<",
                    )
                )
                msg_index += DOUBLE_SIZE_IN_BYTES

            with open(snapshot_dir_path / "translation.json", "w") as writer:
                json.dump(
                    {
                        "x": translation[0],
                        "y": translation[1],
                        "z": translation[2],
                    },
                    writer
                )

        @parser.add_parser("color_image")
        def parse_color_image(
            snapshot_dir_path: Path, color_image_msg: Snapshot
        ):
            msg_index = 0
            color_image_width = from_bytes(
                data=color_image_msg[
                    msg_index:msg_index + UINT32_SIZE_IN_BYTES
                ],
                data_type="uint32",
                endianness="<",
            )
            msg_index += UINT32_SIZE_IN_BYTES
            color_image_height = from_bytes(
                data=color_image_msg[
                    msg_index:msg_index + UINT32_SIZE_IN_BYTES
                ],
                data_type="uint32",
                endianness="<",
            )
            msg_index += UINT32_SIZE_IN_BYTES
            color_image = []

            for _ in range(color_image_width * color_image_height):
                pixel = []
                for _ in range(NUM_BYTES_PIXEL_COLOR_IMAGE):
                    pixel.append(
                        from_bytes(
                            data=color_image_msg[msg_index:msg_index + BYTE_SIZE_IN_BYTES],  # noqa: E501
                            data_type="byte",
                            endianness="<",
                        )
                    )
                    msg_index += BYTE_SIZE_IN_BYTES
                color_image.append(tuple(pixel))

            image = Image.new(
                "RGB",
                (color_image_width, color_image_height),
            )
            image.putdata(color_image)
            image.save(snapshot_dir_path / "color_image.jpg")

        lock = threading.Lock()

        thread_number = 1
        while True:
            client = listener.accept()
            newthread = Handler(
                client=client,
                data_dir=data_dir,
                lock=lock,
                parser=parser,
                thread_number=thread_number,
            )
            newthread.start()
            thread_number += 1
