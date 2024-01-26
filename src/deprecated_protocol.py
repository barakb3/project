import datetime as dt

from .constants import (
    CHAR_SIZE_IN_BYTES,
    UINT32_SIZE_IN_BYTES,
    UINT64_SIZE_IN_BYTES,
)
from .utils import from_bytes, to_bytes

NUM_BYTES_PIXEL_COLOR_IMAGE = 3  # RGB format.

EMPTY_TRANSLATION = (0.0, 0.0, 0.0)
EMPTY_ROTATION = (0.0, 0.0, 0.0, 0.0)
EMPTY_DIM = 0
EMPTY_COLOR_IMAGE = b""
EMPTY_DEPTH_IMAGE = ()
EMPTY_FEELINGS = (0.0, 0.0, 0.0, 0.0)


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

        return Config(supported_fields=tuple(supported_fields))


class Snapshot:
    """
    A class representing the third message in the protocol, a snapshot message.
    """
    def __init__(
        self,
        timestamp: int,
        translation: tuple,
        rotation: tuple,
        color_image_width: int,
        color_image_height: int,
        color_image: bytes,
        depth_image_width: int,
        depth_image_height: int,
        depth_image: tuple,
        feelings: tuple,
    ):
        self.timestamp = timestamp
        self.datetime = dt.datetime.fromtimestamp(
            self.timestamp / 1000, tz=dt.timezone.utc
        )
        assert len(translation) == 3
        assert len(rotation) == 4
        assert (
            len(color_image) == NUM_BYTES_PIXEL_COLOR_IMAGE * color_image_width * color_image_height  # noqa: E501
        )
        assert len(depth_image) == depth_image_width * depth_image_height
        assert len(feelings) == 4
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
        return (
            f"{self.__class__.__name__}"
            f"(datetime={self.datetime!r},\n"
            f"translation={{'x': {self.translation[0]}, 'y': {self.translation[1]}, 'z': {self.translation[2]}}},\n"  # noqa: E501
            f"rotation={{'x': {self.rotation[0]}, 'y': {self.rotation[1]}, 'z': {self.rotation[2]}, 'w': {self.rotation[3]}}},\n"  # noqa: E501
            f"color_image=<{self.color_image_width}x{self.color_image_height}>,\n"  # noqa: E501
            f"depth_image=<{self.depth_image_width}x{self.depth_image_height}>,\n"  # noqa: E501
            f"feelings={{'x': {self.feelings[0]}, 'y': {self.feelings[1]}, 'z': {self.feelings[2]}, 'w': {self.feelings[3]}}})"  # noqa: E501
        )

    def __str__(self) -> str:
        return (
            f"{self.datetime:%Y-%m-%d %H:%M:%S:%f}, {self.translation=}, {self.rotation=}, "  # noqa: E501
            f"color_image=<{self.color_image_width}x{self.color_image_height}>, "  # noqa: E501
            f"depth_image=<{self.depth_image_width}x{self.depth_image_height}>, "  # noqa: E501
            f"{self.feelings=}"
        )

    def __eq__(self, other: "Snapshot") -> bool:
        if not isinstance(other, Snapshot):
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

    def serialize(self) -> bytes:
        msg = bytearray()
        msg += to_bytes(
            value=self.timestamp,
            data_type="uint64",
            endianness="<",
        )
        for coordinate in self.translation:
            msg += to_bytes(
                value=coordinate,
                data_type="double",
                endianness="<",
            )
        for coordinate in self.rotation:
            msg += to_bytes(
                value=coordinate,
                data_type="double",
                endianness="<",
            )
        msg += to_bytes(
            value=self.color_image_width,
            data_type="uint32",
            endianness="<",
        )
        msg += to_bytes(
            value=self.color_image_height,
            data_type="uint32",
            endianness="<",
        )
        msg += self.color_image
        msg += to_bytes(
            value=self.depth_image_width,
            data_type="uint32",
            endianness="<",
        )
        msg += to_bytes(
            value=self.depth_image_height,
            data_type="uint32",
            endianness="<",
        )
        for pixel in range(self.depth_image_width * self.depth_image_height):
            msg += to_bytes(
                value=pixel,
                data_type="float",
                endianness="<",
            )
        for feeling in self.rotation:
            msg += to_bytes(
                value=feeling,
                data_type="float",
                endianness="<",
            )
        return msg

    def clone_by_supported_fields(self, supported_fields: tuple) -> "Snapshot":
        if "translation" in supported_fields:
            translation = self.translation
        else:
            translation = EMPTY_TRANSLATION
        if "rotation" in supported_fields:
            rotation = self.rotation
        else:
            rotation = EMPTY_ROTATION
        if "color_image" in supported_fields:
            color_image_width = self.color_image_width
            color_image_height = self.color_image_height
            color_image = self.color_image
        else:
            color_image_width = EMPTY_DIM
            color_image_height = EMPTY_DIM
            color_image = EMPTY_COLOR_IMAGE
        if "depth_image" in supported_fields:
            depth_image_width = self.depth_image_width
            depth_image_height = self.depth_image_height
            depth_image = self.depth_image
        else:
            depth_image_width = EMPTY_DIM
            depth_image_height = EMPTY_DIM
            depth_image = EMPTY_DEPTH_IMAGE
        if "feelings" in supported_fields:
            feelings = self.rotation
        else:
            feelings = EMPTY_FEELINGS
        return Snapshot(
            timestamp=self.timestamp,
            translation=translation,
            rotation=rotation,
            color_image_width=color_image_width,
            color_image_height=color_image_height,
            color_image=color_image,
            depth_image_width=depth_image_width,
            depth_image_height=depth_image_height,
            depth_image=depth_image,
            feelings=feelings,
        )
