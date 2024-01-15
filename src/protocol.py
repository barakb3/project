import datetime as dt
import io
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
        translation: tuple = (0.0, 0.0, 0.0),
        rotation: tuple = (0.0, 0.0, 0.0, 0.0),
        color_image_width: int = 0,
        color_image_height: int = 0,
        color_image: tuple = (),
        depth_image_width: int = 0,
        depth_image_height: int = 0,
        depth_image: tuple = (),
        feelings: tuple = (0.0, 0.0, 0.0, 0.0),
    ):
        self.timestamp = dt.datetime.fromtimestamp(
            timestamp, tz=dt.timezone.utc
        )
        self.translation = translation
        self.rotation = rotation
        self.color_image_width = color_image_width
        self.color_image_height = color_image_height
        self.color_image = color_image
        self.depth_image_width = depth_image_width
        self.depth_image_height = depth_image_height
        self.depth_image = depth_image
        self.feelings = feelings

    def __len__(self) -> int:
        """
        Returns the number of bytes that make up the snapshot.
        """
        return CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT + \
            (NUM_BYTES_PIXEL_COLOR_IMAGE * self.color_image_width * self.color_image_height) + \
            (NUM_BYTES_PIXEL_DEPTH_IMAGE * self.depth_image_width * self.depth_image_height) # noqa E501

    def read_from_file(file: io.BufferedReader) -> Optional[bytes]:
        binary_timestamp = file.read(NUM_BYTES_TIMESTAMP)
        if binary_timestamp == b"":
            # EOF reached.
            return None
        snapshot_blob = bytearray(binary_timestamp)

        snapshot_blob += file.read(NUM_BYTES_TRANSLATION + NUM_BYTES_ROTATION)

        binary_color_image_height = file.read(NUM_BYTES_DIMENSION)
        binary_color_image_width = file.read(NUM_BYTES_DIMENSION)
        snapshot_blob += binary_color_image_width
        snapshot_blob += binary_color_image_height
        color_image_width = from_bytes(
            data=binary_color_image_width, data_type="uint32", endianness="<"
        )
        color_image_height = from_bytes(
            data=binary_color_image_height, data_type="uint32", endianness="<"
        )
        snapshot_blob += from_bgr_to_rgb(
            bgr=file.read(
                NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height # noqa E501
            )
        )

        binary_depth_image_height = file.read(NUM_BYTES_DIMENSION)
        binary_depth_image_width = file.read(NUM_BYTES_DIMENSION)
        snapshot_blob += binary_depth_image_width
        snapshot_blob += binary_depth_image_height
        depth_image_height = from_bytes(
            data=binary_depth_image_height, data_type="uint32", endianness="<"
        )
        depth_image_width = from_bytes(
            data=binary_depth_image_width, data_type="uint32", endianness="<"
        )
        snapshot_blob += file.read(
            NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height # noqa E501
        )

        snapshot_blob += file.read(NUM_BYTES_FEELINGS)

        return bytes(snapshot_blob)


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


def to_bytes(value: Union[int, float, str],
             data_type: str,
             endianness: str,
             num_bytes: Optional[int] = None) -> bytes:
    """
    Convert values to binary data using `struct.pack` for various data types.

    Args:
        value (Union[int, float, str]): The value to convert.
        data_type (str): The data type to interpret. Supported values:
        'uint64', 'uint32', 'float', 'double', 'char', 'string'.
        endianness (str): Use `<` for little-endian, '>' for big-endian or '='
        for the system's default endianness.
        num_bytes (Optional[int]): Number of bytes to write for the `string`
        type. Otherwise, writes the whole value as a string.

    Returns:
        bytes: The binary representation of the value.
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
        packed_value = struct.pack(
            f"{endianness}{code}", value.encode("utf-8")
        )
    elif data_type == "string":
        value = value.encode("utf-8")
        num_bytes = len(value) if num_bytes is None else num_bytes
        packed_value = struct.pack(
            f"{endianness}{code}".format(num_bytes), value[:num_bytes]
        )
    else:
        packed_value = struct.pack(f"{endianness}{code}", value)

    return packed_value


def from_bgr_to_rgb(bgr: bytes) -> bytes:
    rgb = bytearray()
    for i in range(0, len(bgr), NUM_BYTES_PIXEL_COLOR_IMAGE):
        pixel = bgr[i:i + 3]
        rgb.extend(reversed(pixel))
    return rgb
