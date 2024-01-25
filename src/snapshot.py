import datetime as dt
import struct

from project_pb2 import (
    ColorImage,
    DepthImage,
    Feelings,
    Pose,
    ProtoSnapshot,
    ProtoUserInformation,
)

NUM_BYTES_PIXEL_COLOR_IMAGE = 3  # RGB format.

EMPTY_TRANSLATION = (0.0, 0.0, 0.0)
EMPTY_ROTATION = (0.0, 0.0, 0.0, 0.0)
EMPTY_DIM = 0
EMPTY_COLOR_IMAGE = b""
EMPTY_DEPTH_IMAGE = ()
EMPTY_FEELINGS = (0.0, 0.0, 0.0, 0.0)


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
            f"feelings={{'hunger': {self.feelings[0]}, 'thirst': {self.feelings[1]}, 'exhaustion': {self.feelings[2]}, 'happiness': {self.feelings[3]}}})"  # noqa: E501
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
        equal_fields = [
            self.timestamp == other.timestamp,
            self.translation == other.translation,
            self.rotation == other.rotation,
            self.color_image_width == other.color_image_width,
            self.color_image_height == other.color_image_height,
            self.color_image == other.color_image,
            self.depth_image_width == other.depth_image_width,
            self.depth_image_height == other.depth_image_height,
            self.depth_image == other.depth_image,
            self.feelings == other.feelings
        ]
        fields = [
            "timestamp",
            "translation",
            "rotation",
            "color_image_width",
            "color_image_height",
            "color_image",
            "depth_image_width",
            "depth_image_height",
            "depth_image",
            "feelings",
        ]
        if all(equal_fields):
            return True
        else:
            unequal_fields = [
                field for field, equal in zip(fields, equal_fields)
                if not equal
            ]
            unequal_fields_description = ", ".join(unequal_fields)
            print(
                f"The following fields are not equal: "
                f"{unequal_fields_description}"
            )
            return False

    def __getitem__(self, key: str):  # noqa: ANN204
        return getattr(self, key)

    @classmethod
    def from_parsed(cls, parsed: ProtoSnapshot) -> "Snapshot":
        return cls(
            timestamp=parsed.datetime,
            translation=(
                parsed.pose.translation.x,
                parsed.pose.translation.y,
                parsed.pose.translation.z,
            ),
            rotation=(
                parsed.pose.rotation.x,
                parsed.pose.rotation.y,
                parsed.pose.rotation.z,
                parsed.pose.rotation.w,
            ),
            color_image_width=parsed.color_image.width,
            color_image_height=parsed.color_image.height,
            color_image=parsed.color_image.data,
            depth_image_width=parsed.depth_image.width,
            depth_image_height=parsed.depth_image.height,
            depth_image=tuple(parsed.depth_image.data),
            feelings=(
                round(parsed.feelings.hunger, 6),
                round(parsed.feelings.thirst, 6),
                round(parsed.feelings.exhaustion, 6),
                round(parsed.feelings.happiness, 6),
            ),
        )

    def serialize(self, user_information: tuple) -> bytes:
        if user_information.gender == "m":
            gender = ProtoUserInformation.Gender.MALE
        elif user_information.gender == "f":
            gender = ProtoUserInformation.Gender.FEMALE
        elif user_information.gender == "o":
            gender = ProtoUserInformation.Gender.OTHER
        proto_user_information = ProtoUserInformation(
            user_id=user_information.id,
            username=user_information.username,
            birthday=user_information.birthday,
            gender=gender,
        )
        proto_snapshot = ProtoSnapshot(
            datetime=self.timestamp,
            pose=Pose(
                translation=Pose.Translation(
                    x=self.translation[0],
                    y=self.translation[1],
                    z=self.translation[2],
                ),
                rotation=Pose.Rotation(
                    x=self.rotation[0],
                    y=self.rotation[1],
                    z=self.rotation[2],
                    w=self.rotation[3],
                ),
            ),
            color_image=ColorImage(
                width=self.color_image_width,
                height=self.color_image_height,
                data=self.color_image,
            ),
            depth_image=DepthImage(
                width=self.depth_image_width,
                height=self.depth_image_height,
                data=self.depth_image,
            ),
            feelings=Feelings(
                hunger=self.feelings[0],
                thirst=self.feelings[1],
                exhaustion=self.feelings[2],
                happiness=self.feelings[3],
            ),
        )
        msg = bytearray()
        msg += struct.pack("<I", proto_user_information.ByteSize())
        msg += proto_user_information.SerializeToString()
        msg += struct.pack("<I", proto_snapshot.ByteSize())
        msg += proto_snapshot.SerializeToString()
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
