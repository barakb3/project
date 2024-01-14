import io
import os
import struct
from typing import Optional, Union

from .constants import (
    DOUBLE_SIZE_IN_BYTES,
    FLOAT_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)

NUM_BYTES_TIMESTAMP = UINT64_SIZE_IN_BYTES
NUM_BYTES_TRANSLATION = 3 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_ROTATION = 4 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_DIMENSION = UINT32_SIZE_IN_BYTES
NUM_BYTES_FEELINGS = 4 * FLOAT_SIZE_IN_BYTES
NUM_BYTES_PIXEL_COLOR_IMAGE = 3  # RGB format.
NUM_BYTES_PIXEL_DEPTH_IMAGE = FLOAT_SIZE_IN_BYTES
CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT = NUM_BYTES_TIMESTAMP + \
    NUM_BYTES_TRANSLATION + \
    NUM_BYTES_ROTATION + \
    (4 * NUM_BYTES_DIMENSION) + \
    NUM_BYTES_FEELINGS


class Hello:
    # TODO: implement this class as part of exercise 6.
    pass


class Config:
    # TODO: implement this class as part of exercise 6.
    pass


class Snapshot:
    # TODO: Document this class.
    def __init__(
            self,
            timestamp: int,
            color_image_width: int,
            color_image_height: int,
            depth_image_width: int,
            depth_image_height: int,
    ):
        self.timestamp = timestamp
        self.color_image_width = color_image_width
        self.color_image_height = color_image_height
        self.depth_image_width = depth_image_width
        self.depth_image_height = depth_image_height

    def __len__(self) -> int:
        """
        Returns the number of bytes that make up the snapshot.
        """
        return CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT + \
            (NUM_BYTES_PIXEL_COLOR_IMAGE * self.color_image_width * self.color_image_height) + \
            (NUM_BYTES_PIXEL_DEPTH_IMAGE * self.depth_image_width * self.depth_image_height) # noqa E501

    def read_from_file(file: io.BufferedReader) -> Optional["Snapshot"]:
        binary_timestamp = file.read(NUM_BYTES_TIMESTAMP)
        if binary_timestamp == b"":
            # EOF reached.
            return None

        timestamp = from_bytes(
            data=binary_timestamp,
            data_type="uint64",
            endianness="<",
        )

        # Jump to color image dimensions.
        file.seek(NUM_BYTES_TRANSLATION + NUM_BYTES_ROTATION, os.SEEK_CUR)

        color_image_height = from_bytes(
            data=file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        color_image_width = from_bytes(
            data=file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )

        # Jump to depth image dimensions.
        file.seek(
            NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height, # noqa E501
            os.SEEK_CUR,
        )
        depth_image_height = from_bytes(
            data=file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        depth_image_width = from_bytes(
            data=file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )

        # Jump to the end of the snapshot.
        file.seek(
            NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height + NUM_BYTES_FEELINGS, # noqa E501
            os.SEEK_CUR,
        )

        return Snapshot(
            timestamp=timestamp,
            color_image_width=color_image_width,
            color_image_height=color_image_height,
            depth_image_width=depth_image_width,
            depth_image_height=depth_image_height,
        )


def from_bytes(
        data: bytes,
        data_type: str,
        endianness: str,
        num_bytes: Optional[int] = None
) -> Union[int, float, str]:
    """
    Read binary data using `struct.unpack` for various data types.

    Args:
        data (bytes): The binary data to read from.
        data_type (str): The data type to interpret. Supported values:
        'uint64', 'uint32', 'float', 'double', 'char', 'string'.
        endianness (str): Use `<` for little-endian, '>' for big-endian or '='
        for the system's deafult endianness.
        num_bytes (Optional[int]): Number of bytes to read for the `string`
        type. Otherwise, reads the whole data as a string.

    Returns:
        Union[int, float, str]: The interpreted value.
    """
    type_code = {
        "uint64": "Q",
        "uint32": "I",
        "float": "f",
        "double": "d",
        "char": "c",
        "string": "{}s",
        "byte": "B",
    }

    if data_type not in type_code:
        raise ValueError(f"Unsupported data type: {data_type}.")

    code = type_code[data_type]

    if data_type == "char":
        unpacked_value = struct.unpack(
            f"{endianness}{code}", data[:1]
        )[0].decode("utf-8")
    elif data_type == "string":
        num_bytes = len(data) if num_bytes is None else num_bytes
        unpacked_value = struct.unpack(
            f"{endianness}{code}".format(num_bytes), data[:num_bytes]
        )[0].decode("utf-8")
    else:
        unpacked_value = struct.unpack(
            f"{endianness}{code}", data[:struct.calcsize(code)]
        )[0]

    return unpacked_value
