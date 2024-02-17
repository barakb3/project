import struct

from project_pb2 import ProtoUserInformation

import pytest

from src.user_information import UserInformation

ID = 3
NAME = "Barak Basson"
BIRTHDAY = 699746400


@pytest.mark.parametrize("gender", ["m", "f", "o"])
def test_serialize(gender: str):
    user_information = UserInformation(
        id=ID,
        username=NAME,
        birthday=BIRTHDAY,
        gender=gender,
    )
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
    serialized = []
    serialized.append(struct.pack("<I", proto_user_information.ByteSize()))
    serialized.append(proto_user_information.SerializeToString())
    assert (
        user_information.serialize() == b"".join(serialized)
    )
