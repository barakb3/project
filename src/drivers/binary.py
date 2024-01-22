import io
from collections import namedtuple

from ..constants import (
    CHAR_SIZE_IN_BYTES,
    DOUBLE_SIZE_IN_BYTES,
    FLOAT_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from ..protocol import Snapshot, SnapshotBinaryBlob, SnapshotMetadata
from ..utils import from_bytes

NUM_BYTES_TIMESTAMP = UINT64_SIZE_IN_BYTES
NUM_BYTES_TRANSLATION = 3 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_ROTATION = 4 * DOUBLE_SIZE_IN_BYTES
NUM_BYTES_DIMENSION = UINT32_SIZE_IN_BYTES
NUM_BYTES_FEELINGS = 4 * FLOAT_SIZE_IN_BYTES
NUM_BYTES_PIXEL_COLOR_IMAGE = 3  # RGB format.
NUM_BYTES_PIXEL_DEPTH_IMAGE = FLOAT_SIZE_IN_BYTES


class BinaryDriver:
    def __init__(self, path: str):
        self.file: io.BufferedReader = open(path, "rb")

    def get_user_information(self) -> tuple:
        user_information = namedtuple(
            "user_information", ["id", "username", "birthday", "gender"]
        )
        user_information.id: int = from_bytes(
            data=self.file.read(UINT64_SIZE_IN_BYTES),
            data_type="uint64",
            endianness="<",
        )
        name_length: int = from_bytes(
            data=self.file.read(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        user_information.username: str = from_bytes(
            data=self.file.read(name_length),
            data_type="string",
            endianness="<",
        )
        user_information.birthday: int = from_bytes(
            data=self.file.read(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        user_information.gender: str = from_bytes(
            data=self.file.read(CHAR_SIZE_IN_BYTES),
            data_type="char",
            endianness="<",
        )
        return user_information

    def get_snapshot(self) -> Snapshot:
        binary_timestamp = self.file.read(NUM_BYTES_TIMESTAMP)
        if binary_timestamp == b"":
            # EOF reached.
            return None
        timestamp = from_bytes(
            data=binary_timestamp, data_type="uint64", endianness="<"
        )
        binary_translation = self.file.read(NUM_BYTES_TRANSLATION)
        binary_rotation = self.file.read(NUM_BYTES_ROTATION)
        binary_color_image_height = self.file.read(NUM_BYTES_DIMENSION)
        color_image_height = from_bytes(
            data=binary_color_image_height, data_type="uint32", endianness="<"
        )
        binary_color_image_width = self.file.read(NUM_BYTES_DIMENSION)
        color_image_width = from_bytes(
            data=binary_color_image_width, data_type="uint32", endianness="<"
        )
        binary_color_image = from_bgr_to_rgb(
            bgr=self.file.read(
                NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
            )
        )
        assert (
            len(binary_color_image) == NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
        )
        binary_depth_image_height = self.file.read(NUM_BYTES_DIMENSION)
        depth_image_height = from_bytes(
            data=binary_depth_image_height, data_type="uint32", endianness="<"
        )
        binary_depth_image_width = self.file.read(NUM_BYTES_DIMENSION)
        depth_image_width = from_bytes(
            data=binary_depth_image_width, data_type="uint32", endianness="<"
        )
        binary_depth_image = self.file.read(
            NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height  # noqa: E501
        )
        assert (
            len(binary_depth_image) == NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height  # noqa: E501
        )
        binary_feelings = self.file.read(NUM_BYTES_FEELINGS)

        binary_blob = SnapshotBinaryBlob(
            timestamp=binary_timestamp,
            translation=binary_translation,
            rotation=binary_rotation,
            color_image_width=binary_color_image_width,
            color_image_height=binary_color_image_height,
            color_image=binary_color_image,
            depth_image_width=binary_depth_image_width,
            depth_image_height=binary_depth_image_height,
            depth_image=binary_depth_image,
            feelings=binary_feelings,
        )
        metadata = SnapshotMetadata(
            timestamp=timestamp,
            color_image_width=color_image_width,
            color_image_height=color_image_height,
            depth_image_width=depth_image_width,
            depth_image_height=depth_image_height,
        )

        return Snapshot(
            binary_blob=binary_blob,
            metadata=metadata,
        )


def from_bgr_to_rgb(bgr: bytes) -> bytes:
    rgb = bytearray()
    for i in range(0, len(bgr), NUM_BYTES_PIXEL_COLOR_IMAGE):
        pixel = bgr[i:i + 3]
        rgb.extend(reversed(pixel))
    return rgb
