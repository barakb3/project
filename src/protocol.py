import datetime as dt
import io
import struct
from typing import Optional, Union

from .constants import (
    BYTE_SIZE_IN_BYTES,
    CHAR_SIZE_IN_BYTES,
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

EMPTY_BINARY_TRANSLATION = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
EMPTY_BINARY_ROTATION = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
EMPTY_BINARY_COLOR_IMAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00"
EMPTY_BINARY_DEPTH_IMAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00"
EMPTY_BINARY_FEELINGS = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501


class Hello:
    """
    A class representing the first message in the protocol, a hello message.
    """
    def __init__(
        self, user_id: int, username: str, birthday: int, gender: str
    ):
        self.user_id = user_id
        self.username = username
        self.birthday = birthday
        self.gender = gender

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(user_id={self.user_id!r}, "
            f"username={self.username!r}, "
            f"birthday={self.birthday!r}, "
            f"gender={self.gender!r})"
        )

    def __str__(self) -> str:
        return (
            f"[{self.user_id=}] "
            f"{self.username=}: Date of birth: "
            f"{self.birthday}, {self.gender=}"
        )

    def __eq__(self, other: "Hello") -> bool:
        if not isinstance(other, Hello):
            return NotImplemented
        return self.user_id == other.user_id and \
            self.username == other.username and \
            self.birthday == other.birthday and \
            self.gender == other.gender

    def serialize(self) -> bytes:
        serialized = to_bytes(
            value=self.user_id, data_type="uint64", endianness="<"
        )
        serialized += to_bytes(
            value=len(self.username), data_type="uint32", endianness="<"
        )
        serialized += to_bytes(
            value=self.username, data_type="string", endianness="<"
        )
        serialized += to_bytes(
            value=self.birthday, data_type="uint32", endianness="<"
        )
        serialized += to_bytes(
            value=self.gender, data_type="char", endianness="<"
        )
        return serialized

    def deserialize(msg: bytes) -> "Hello":
        data_index = 0

        user_id = from_bytes(
            data=msg[data_index:data_index + UINT64_SIZE_IN_BYTES],
            data_type="uint64",
            endianness="<",
        )
        data_index += UINT64_SIZE_IN_BYTES

        username_length = from_bytes(
            data=msg[data_index:data_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        data_index += UINT32_SIZE_IN_BYTES

        username = from_bytes(
            data=msg[data_index:data_index + username_length],
            data_type="string",
            endianness="<",
        )
        data_index += username_length

        birthday = from_bytes(
            data=msg[data_index:data_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        data_index += UINT32_SIZE_IN_BYTES

        gender = from_bytes(
            data=msg[data_index:data_index + CHAR_SIZE_IN_BYTES],
            data_type="char",
            endianness="<"
        )
        data_index += CHAR_SIZE_IN_BYTES

        assert (
            data_index == len(msg)
        ), "Message length received doesn't match."

        return Hello(
            user_id=user_id,
            username=username,
            birthday=birthday,
            gender=gender,
        )


class Config:
    """
    A class representing the second message in the protocol, a config message.
    """
    def __init__(self, supported_fields: tuple):
        self.supported_fields = supported_fields

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(supported_fields={self.supported_fields!r})"
        )

    def __str__(self) -> str:
        return (
            f"Configuration: {self.supported_fields=}"
        )

    def __eq__(self, other: "Config") -> bool:
        if not isinstance(other, Config):
            return NotImplemented
        return self.supported_fields == other.supported_fields

    def serialize(self) -> bytes:
        serialized = to_bytes(
            value=len(self.supported_fields),
            data_type="uint32",
            endianness="<",
        )
        for field in self.supported_fields:
            serialized += to_bytes(
                value=len(field), data_type="uint32", endianness="<"
            )
            serialized += to_bytes(
                value=field, data_type="string", endianness="<"
            )
        return serialized

    def deserialize(msg: bytes) -> "Config":
        data_index = 0

        num_supported_fields = from_bytes(
            data=msg[data_index:data_index + UINT32_SIZE_IN_BYTES],
            data_type="uint32",
            endianness="<",
        )
        data_index += UINT32_SIZE_IN_BYTES

        supported_fields = []
        for _ in range(num_supported_fields):
            field_len = from_bytes(
                data=msg[data_index:data_index + UINT32_SIZE_IN_BYTES],
                data_type="uint32",
                endianness="<",
            )
            data_index += UINT32_SIZE_IN_BYTES

            supported_fields.append(
                from_bytes(
                    data=msg[data_index:data_index + field_len],
                    data_type="string",
                    endianness="<",
                )
            )
            data_index += field_len

        assert (
            data_index == len(msg)
        ), "Message length received doesn't match."

        return Config(supported_fields=supported_fields)


class SnapshotBinaryBlob:
    def __init__(
        self,
        timestamp: bytes,
        translation: bytes,
        rotation: bytes,
        color_image_width: bytes,
        color_image_height: bytes,
        color_image: bytes,
        depth_image_width: bytes,
        depth_image_height: bytes,
        depth_image: bytes,
        feelings: bytes,
    ):
        assert len(timestamp) == NUM_BYTES_TIMESTAMP
        assert (
            len(translation) == NUM_BYTES_TRANSLATION
        ), "Translation tuple is of length 3."
        assert (
            len(rotation) == NUM_BYTES_ROTATION
        ), "Rotation tuple is of length 4."
        assert len(color_image_width) == NUM_BYTES_DIMENSION
        assert len(color_image_height) == NUM_BYTES_DIMENSION
        assert len(depth_image_width) == NUM_BYTES_DIMENSION
        assert len(depth_image_height) == NUM_BYTES_DIMENSION
        assert (
            len(feelings) == NUM_BYTES_FEELINGS
        ), "Feelings tuple is of length 4."

        self.timestamp = timestamp
        self.translation = translation
        self.rotation = rotation
        self.color_image_width = color_image_width
        self.color_image_height = color_image_height
        self.color_image = color_image
        self.depth_image_width = depth_image_width
        self.depth_image_height = depth_image_height
        self.depth_image = depth_image
        self.feelings = feelings

    def __repr__(self) -> str:
        splitted_color_image = []
        for i in range(len(self.color_image)), 3 * BYTE_SIZE_IN_BYTES:
            splitted_color_image.append(
                self.color_image[i:i + (3 * BYTE_SIZE_IN_BYTES)]
            )
        splitted_depth_image = []
        for i in range(len(self.depth_image)), FLOAT_SIZE_IN_BYTES:
            splitted_depth_image.append(
                self.depth_image[i:i + FLOAT_SIZE_IN_BYTES]
            )

        return (
            f"{self.__class__.__name__}\n"
            f"(timestamp={self.timestamp!r}, \n"
            f"translation={self.translation[0:UINT64_SIZE_IN_BYTES]!r} \n"
            f"{self.translation[UINT64_SIZE_IN_BYTES:2 * UINT64_SIZE_IN_BYTES]!r}\n"  # noqa: E501
            f"{self.translation[2 * UINT64_SIZE_IN_BYTES:3 * UINT64_SIZE_IN_BYTES]!r},\n"  # noqa: E501
            f"rotation={self.rotation[0:UINT64_SIZE_IN_BYTES]!r} \n"
            f"{self.rotation[UINT64_SIZE_IN_BYTES:2 * UINT64_SIZE_IN_BYTES]!r}\n"  # noqa: E501
            f"{self.rotation[2 * UINT64_SIZE_IN_BYTES:3 * UINT64_SIZE_IN_BYTES]!r}\n"  # noqa: E501
            f"{self.rotation[3 * UINT64_SIZE_IN_BYTES:4 * UINT64_SIZE_IN_BYTES]!r}, \n"  # noqa: E501
            f"color_image_width={self.color_image_width!r}, \n"
            f"color_image_height={self.color_image_height!r}, \n"
            f"color_image={splitted_color_image!r}, \n"
            f"depth_image_width={self.depth_image_width!r}, \n"
            f"depth_image_height={self.depth_image_height!r}, \n"
            f"depth_image={splitted_depth_image!r}, \n"
            f"feelings={self.feelings[0:FLOAT_SIZE_IN_BYTES]!r} \n"
            f"{self.feelings[FLOAT_SIZE_IN_BYTES:2 * FLOAT_SIZE_IN_BYTES]!r}\n"
            f"{self.feelings[2 * UINT64_SIZE_IN_BYTES:3 * FLOAT_SIZE_IN_BYTES]!r}\n"  # noqa: E501
            f"{self.feelings[3 * FLOAT_SIZE_IN_BYTES:4 * FLOAT_SIZE_IN_BYTES]!r})"  # noqa: E501
        )

    def __str__(self) -> str:
        datetime = dt.datetime.fromtimestamp(
            self.timestamp / 1000, tz=dt.timezone.utc
        )
        return (
            f"A binary representation of a snapshot from: "
            f"[{datetime::%Y-%m-%d %H:%M:%S:%f}]"
        )

    def __eq__(self, other: "SnapshotBinaryBlob") -> bool:
        if not isinstance(other, SnapshotBinaryBlob):
            return NotImplemented
        return self.timestamp == other.timestamp and \
            self.translation == other.translation and \
            self.rotation == other.rotation and \
            self.color_image_width == other.color_image_width and \
            self.color_image_height == other.color_image_height and \
            self.color_image == other.color_image and \
            self.depth_image_width == other.depth_image_width and \
            self.depth_image_height == other.depth_image_height and \
            self.depth_image == other.depth_image and \
            self.feelings == other.feelings


class SnapshotMetadata:
    def __init__(
        self,
        timestamp: int,
        color_image_width: int,
        color_image_height: int,
        depth_image_width: int,
        depth_image_height: int,
    ):
        self.timestamp = timestamp
        self.datetime = dt.datetime.fromtimestamp(
            self.timestamp / 1000, tz=dt.timezone.utc
        )
        self.color_image_width = color_image_width
        self.color_image_height = color_image_height
        self.depth_image_width = depth_image_width
        self.depth_image_height = depth_image_height

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(timestamp_millisec={self.timestamp!r}, "
            f"datetime={self.datetime!r}, "
            f"color_image_width={self.color_image_width!r}, "
            f"color_image_height={self.color_image_height!r}, "
            f"depth_image_width={self.depth_image_width!r}, "
            f"depth_image_height={self.depth_image_height!r})"
        )

    def __str__(self) -> str:
        return (
            f"The metadata of the snapshot: "
            f"[{self.datetime:%Y-%m-%d %H:%M:%S:%f}] "
            f"<Image color "
            f"{self.color_image_width} x {self.color_image_height}> "
            f"<Depth color "
            f"{self.depth_image_width} x {self.depth_image_height}>"
        )

    def __eq__(self, other: "SnapshotMetadata") -> bool:
        if not isinstance(other, SnapshotMetadata):
            return NotImplemented
        return self.timestamp == other.timestamp and \
            self.datetime == other.datetime and \
            self.color_image_width == other.color_image_width and \
            self.color_image_height == other.color_image_height and \
            self.depth_image_width == other.depth_image_width and \
            self.depth_image_height == other.depth_image_height


class Snapshot:
    """
    A class representing the third message in the protocol, a snapshot message.
    """
    def __init__(
        self,
        binary_blob: SnapshotBinaryBlob,
        metadata: SnapshotMetadata,
    ):
        self.binary_blob = binary_blob
        self.metadata = metadata

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(binary_blob={self.binary_blob!r},\n"
            f"metadata={self.metadata!r})"
        )

    def __str__(self) -> str:
        return (
            f"A snapshot:\n"
            f"{self.binary_blob},\n"
            f"{self.metadata}"
        )

    def __len__(self) -> int:
        """
        Returns the number of bytes that make up the snapshot.
        """
        return CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT + \
            (NUM_BYTES_PIXEL_COLOR_IMAGE * self.metadata.color_image_width * self.metadata.color_image_height) + \
            (NUM_BYTES_PIXEL_DEPTH_IMAGE * self.metadata.depth_image_width * self.metadata.depth_image_height)  # noqa: E501

    def __eq__(self, other: "Snapshot") -> bool:
        if not isinstance(other, Snapshot):
            return NotImplemented
        return self.binary_blob == other.binary_blob and \
            self.metadata == other.metadata

    @property
    def timestamp(self) -> str:
        return f"{self.metadata.datetime:%Y-%m-%d_%H-%M-%S-%f}"

    def get_supported_fields_msg(self, supported_fields: tuple) -> bytes:
        msg = bytearray()
        msg += self.binary_blob.timestamp
        if "translation" in supported_fields:
            msg += self.binary_blob.translation
        else:
            msg += EMPTY_BINARY_TRANSLATION
        if "rotation" in supported_fields:
            msg += self.binary_blob.rotation
        else:
            msg += EMPTY_BINARY_ROTATION
        if "color_image" in supported_fields:
            msg += self.binary_blob.color_image_width + \
                self.binary_blob.color_image_height + \
                self.binary_blob.color_image
        else:
            msg += EMPTY_BINARY_COLOR_IMAGE
        if "depth_image" in supported_fields:
            msg += self.binary_blob.depth_image_width + \
                self.binary_blob.depth_image_height + \
                self.binary_blob.depth_image
        else:
            msg += EMPTY_BINARY_DEPTH_IMAGE
        if "feelings" in supported_fields:
            msg += self.binary_blob.feelings
        else:
            msg += EMPTY_BINARY_FEELINGS
        return msg

    def read_from_file(file: io.BufferedReader) -> Optional["Snapshot"]:
        binary_timestamp = file.read(NUM_BYTES_TIMESTAMP)
        if binary_timestamp == b"":
            # EOF reached.
            return None
        timestamp = from_bytes(
            data=binary_timestamp, data_type="uint64", endianness="<"
        )
        binary_translation = file.read(NUM_BYTES_TRANSLATION)
        binary_rotation = file.read(NUM_BYTES_ROTATION)
        binary_color_image_height = file.read(NUM_BYTES_DIMENSION)
        color_image_height = from_bytes(
            data=binary_color_image_height, data_type="uint32", endianness="<"
        )
        binary_color_image_width = file.read(NUM_BYTES_DIMENSION)
        color_image_width = from_bytes(
            data=binary_color_image_width, data_type="uint32", endianness="<"
        )
        binary_color_image = from_bgr_to_rgb(
            bgr=file.read(
                NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
            )
        )
        assert (
            len(binary_color_image) == NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
        )
        binary_depth_image_height = file.read(NUM_BYTES_DIMENSION)
        depth_image_height = from_bytes(
            data=binary_depth_image_height, data_type="uint32", endianness="<"
        )
        binary_depth_image_width = file.read(NUM_BYTES_DIMENSION)
        depth_image_width = from_bytes(
            data=binary_depth_image_width, data_type="uint32", endianness="<"
        )
        binary_depth_image = file.read(
            NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height  # noqa: E501
        )
        assert (
            len(binary_depth_image) == NUM_BYTES_PIXEL_DEPTH_IMAGE * depth_image_width * depth_image_height  # noqa: E501
        )
        binary_feelings = file.read(NUM_BYTES_FEELINGS)

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
