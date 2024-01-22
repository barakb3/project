import io
from collections import namedtuple

from project_pb2 import ProtoSnapshot, ProtoUserInformation

from ..constants import UINT32_SIZE_IN_BYTES
from ..protocol import Snapshot
from ..utils import from_bytes


class ProtobufDriver:
    def __init__(self, path: str):
        self.file: io.BufferedReader = open(path, "rb")

    def get_user_information(self) -> tuple:
        size = from_bytes(
            data=self.file.read(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        parsed = ProtoUserInformation()
        parsed.ParseFromString(self.file.read(size))
        UserInformation = namedtuple(
            "user_information", ["id", "username", "birthday", "gender"]
        )
        if parsed.gender == ProtoUserInformation.Gender.MALE:
            gender = "m"
        elif parsed.gender == ProtoUserInformation.Gender.FEMALE:
            gender = "f"
        elif parsed.gender == ProtoUserInformation.Gender.OTHER:
            gender = "o"

        user_information = UserInformation(
            id=parsed.user_id,
            username=parsed.username,
            birthday=parsed.birthday,
            gender=gender,
        )
        return user_information

    def get_snapshot(self) -> Snapshot:
        binary_size = self.file.read(UINT32_SIZE_IN_BYTES)
        if binary_size == b"":
            # EOF reached.
            self.file.close()
            return None
        size = from_bytes(
            data=binary_size,
            data_type="uint32",
            endianness="<",
        )
        parsed = ProtoSnapshot()
        parsed.ParseFromString(self.file.read(size))
        return Snapshot(
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
                parsed.feelings.hunger,
                parsed.feelings.thirst,
                parsed.feelings.exhaustion,
                parsed.feelings.happiness,
            ),
        )
