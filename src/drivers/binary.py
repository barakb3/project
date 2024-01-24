import io
from collections import namedtuple

from ..constants import (
    CHAR_SIZE_IN_BYTES,
    DOUBLE_SIZE_IN_BYTES,
    FLOAT_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from ..snapshot import Snapshot
from ..utils import from_bytes

NUM_BYTES_TIMESTAMP = UINT64_SIZE_IN_BYTES
NUM_BYTES_DIMENSION = UINT32_SIZE_IN_BYTES
NUM_BYTES_PIXEL_COLOR_IMAGE = 3  # RGB format.


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
            self.file.close()
            return None
        timestamp = from_bytes(
            data=binary_timestamp, data_type="uint64", endianness="<"
        )
        Translation = namedtuple("translation", ["x", "y", "z"])
        translation = Translation(
            x=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
            y=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
            z=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
        )
        Rotation = namedtuple("rotation", ["x", "y", "z", "w"])
        rotation = Rotation(
            x=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
            y=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
            z=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
            w=from_bytes(
                data=self.file.read(DOUBLE_SIZE_IN_BYTES),
                data_type="double",
                endianness="<",
            ),
        )
        color_image_height = from_bytes(
            data=self.file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        color_image_width = from_bytes(
            data=self.file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        color_image = from_bgr_to_rgb(
            bgr=self.file.read(
                NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
            )
        )
        assert (
            len(color_image) == NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
        )
        depth_image_height = from_bytes(
            data=self.file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        depth_image_width = from_bytes(
            data=self.file.read(NUM_BYTES_DIMENSION),
            data_type="uint32",
            endianness="<",
        )
        depth_image = []
        for _ in range(depth_image_width * depth_image_height):
            depth_image.append(
                from_bytes(
                    data=self.file.read(FLOAT_SIZE_IN_BYTES),
                    data_type="float",
                    endianness="<",
                )
            )
        Feelings = namedtuple(
            "feelings", ["hunger", "thirst", "exhaustion", "happiness"]
        )
        feelings = Feelings(
            hunger=from_bytes(
                data=self.file.read(FLOAT_SIZE_IN_BYTES),
                data_type="float",
                endianness="<",
            ),
            thirst=from_bytes(
                data=self.file.read(FLOAT_SIZE_IN_BYTES),
                data_type="float",
                endianness="<",
            ),
            exhaustion=from_bytes(
                data=self.file.read(FLOAT_SIZE_IN_BYTES),
                data_type="float",
                endianness="<",
            ),
            happiness=from_bytes(
                data=self.file.read(FLOAT_SIZE_IN_BYTES),
                data_type="float",
                endianness="<",
            ),
        )

        return Snapshot(
            timestamp=timestamp,
            translation=translation,
            rotation=rotation,
            color_image_width=color_image_width,
            color_image_height=color_image_height,
            color_image=color_image,
            depth_image_width=depth_image_width,
            depth_image_height=depth_image_height,
            depth_image=tuple(depth_image),
            feelings=feelings,
        )


def from_bgr_to_rgb(bgr: bytes) -> bytes:
    rgb = bytearray()
    for i in range(0, len(bgr), NUM_BYTES_PIXEL_COLOR_IMAGE):
        pixel = bgr[i:i + 3]
        rgb.extend(reversed(pixel))
    return rgb
