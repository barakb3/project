import struct

from project_pb2 import ProtoUserInformation


class UserInformation:
    """
    A class representing the user information.
    """
    def __init__(self, id: int, username: str, birthday: int, gender: str):
        self.id = id
        self.username = username
        self.birthday = birthday
        self.gender = gender

    @classmethod
    def from_parsed(cls, parsed: ProtoUserInformation) -> "UserInformation":
        if parsed.gender == ProtoUserInformation.Gender.MALE:
            gender = "m"
        elif parsed.gender == ProtoUserInformation.Gender.FEMALE:
            gender = "f"
        elif parsed.gender == ProtoUserInformation.Gender.OTHER:
            gender = "o"

        return cls(
            id=parsed.user_id,
            username=parsed.username,
            birthday=parsed.birthday,
            gender=gender
        )

    def serialize(self) -> bytes:
        if self.gender == "m":
            gender = ProtoUserInformation.Gender.MALE
        elif self.gender == "f":
            gender = ProtoUserInformation.Gender.FEMALE
        elif self.gender == "o":
            gender = ProtoUserInformation.Gender.OTHER
        proto_user_information = ProtoUserInformation(
            user_id=self.id,
            username=self.username,
            birthday=self.birthday,
            gender=gender,
        )
        return b"".join(
            [
                struct.pack("<I", proto_user_information.ByteSize()),
                proto_user_information.SerializeToString(),
            ]
        )
