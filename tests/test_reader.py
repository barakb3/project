import struct

from furl import furl

from project_pb2 import (
    ColorImage,
    DepthImage,
    Feelings,
    Pose,
    ProtoSnapshot,
    ProtoUserInformation,
)

import pytest

from src.reader import Reader
from src.snapshot import Snapshot

from .test_utils import (
    COLOR_IMAGE_1,
    COLOR_IMAGE_2,
    COLOR_IMAGE_HEIGHT_1,
    COLOR_IMAGE_HEIGHT_2,
    COLOR_IMAGE_WIDTH_1,
    COLOR_IMAGE_WIDTH_2,
    DEPTH_IMAGE_1,
    DEPTH_IMAGE_2,
    DEPTH_IMAGE_HEIGHT_1,
    DEPTH_IMAGE_HEIGHT_2,
    DEPTH_IMAGE_WIDTH_1,
    DEPTH_IMAGE_WIDTH_2,
    FEELINGS_1,
    FEELINGS_2,
    ROTATION_1,
    ROTATION_2,
    TIMESTAMP_1,
    TIMESTAMP_2,
    TRANSLATION_1,
    TRANSLATION_2,
)

ID = 3
NAME = "Barak Basson"
BIRTHDAY = 699746400
GENDER = "m"


def binary_user_information() -> bytes:
    return struct.pack(
        "<QI{}sIc".format(len(NAME)),
        ID,
        len(NAME),
        bytes(NAME, "utf-8"),
        BIRTHDAY,
        bytes(GENDER, "utf-8"),
    )


def protobuf_user_information() -> bytes:
    user_information = ProtoUserInformation(
        user_id=ID,
        username=NAME,
        birthday=BIRTHDAY,
        gender=0,
    )
    return b"".join(
        [
            struct.pack("<I", user_information.ByteSize()),
            user_information.SerializeToString(),
        ]
    )


def binary_snapshot_list() -> bytes:
    snapshot_list = []
    snapshot_list.append(struct.pack("<Q", TIMESTAMP_1))
    for coor in TRANSLATION_1:
        snapshot_list.append(struct.pack("<d", coor))
    for coor in ROTATION_1:
        snapshot_list.append(struct.pack("<d", coor))
    snapshot_list.append(struct.pack("<I", COLOR_IMAGE_HEIGHT_1))
    snapshot_list.append(struct.pack("<I", COLOR_IMAGE_WIDTH_1))
    snapshot_list.append(COLOR_IMAGE_1)
    snapshot_list.append(struct.pack("<I", DEPTH_IMAGE_HEIGHT_1))
    snapshot_list.append(struct.pack("<I", DEPTH_IMAGE_WIDTH_1))
    for pixel in DEPTH_IMAGE_1:
        snapshot_list.append(struct.pack("<f", pixel))
    for feeling in FEELINGS_1:
        snapshot_list.append(struct.pack("<f", feeling))

    snapshot_list.append(struct.pack("<Q", TIMESTAMP_2))
    for coor in TRANSLATION_2:
        snapshot_list.append(struct.pack("<d", coor))
    for coor in ROTATION_2:
        snapshot_list.append(struct.pack("<d", coor))
    snapshot_list.append(struct.pack("<I", COLOR_IMAGE_HEIGHT_2))
    snapshot_list.append(struct.pack("<I", COLOR_IMAGE_WIDTH_2))
    snapshot_list.append(COLOR_IMAGE_2)
    snapshot_list.append(struct.pack("<I", DEPTH_IMAGE_HEIGHT_2))
    snapshot_list.append(struct.pack("<I", DEPTH_IMAGE_WIDTH_2))
    for pixel in DEPTH_IMAGE_2:
        snapshot_list.append(struct.pack("<f", pixel))
    for feeling in FEELINGS_2:
        snapshot_list.append(struct.pack("<f", feeling))

    return b"".join(snapshot_list)


def protobuf_snapshot_list() -> bytes:
    snapshot_1 = ProtoSnapshot(
        datetime=TIMESTAMP_1,
        pose=Pose(
            translation=Pose.Translation(
                x=TRANSLATION_1[0],
                y=TRANSLATION_1[1],
                z=TRANSLATION_1[2],
            ),
            rotation=Pose.Rotation(
                x=ROTATION_1[0],
                y=ROTATION_1[1],
                z=ROTATION_1[2],
                w=ROTATION_1[3],
            ),
        ),
        color_image=ColorImage(
            width=COLOR_IMAGE_WIDTH_1,
            height=COLOR_IMAGE_HEIGHT_1,
            data=COLOR_IMAGE_1,
        ),
        depth_image=DepthImage(
            width=DEPTH_IMAGE_WIDTH_1,
            height=DEPTH_IMAGE_HEIGHT_1,
            data=DEPTH_IMAGE_1,
        ),
        feelings=Feelings(
            hunger=FEELINGS_1[0],
            thirst=FEELINGS_1[1],
            exhaustion=FEELINGS_1[2],
            happiness=FEELINGS_1[3],
        ),
    )

    snapshot_2 = ProtoSnapshot(
        datetime=TIMESTAMP_2,
        pose=Pose(
            translation=Pose.Translation(
                x=TRANSLATION_2[0],
                y=TRANSLATION_2[1],
                z=TRANSLATION_2[2],
            ),
            rotation=Pose.Rotation(
                x=ROTATION_2[0],
                y=ROTATION_2[1],
                z=ROTATION_2[2],
                w=ROTATION_2[3],
            ),
        ),
        color_image=ColorImage(
            width=COLOR_IMAGE_WIDTH_2,
            height=COLOR_IMAGE_HEIGHT_2,
            data=COLOR_IMAGE_2,
        ),
        depth_image=DepthImage(
            width=DEPTH_IMAGE_WIDTH_2,
            height=DEPTH_IMAGE_HEIGHT_2,
            data=DEPTH_IMAGE_2,
        ),
        feelings=Feelings(
            hunger=FEELINGS_2[0],
            thirst=FEELINGS_2[1],
            exhaustion=FEELINGS_2[2],
            happiness=FEELINGS_2[3],
        ),
    )
    msg = []
    msg.append(struct.pack("<I", snapshot_1.ByteSize()))
    msg.append(snapshot_1.SerializeToString())
    msg.append(struct.pack("<I", snapshot_2.ByteSize()))
    msg.append(snapshot_2.SerializeToString())
    return b"".join(msg)


@pytest.fixture(params=[
    ("binary", binary_user_information(), binary_snapshot_list()),
    ("protobuf", protobuf_user_information(), protobuf_snapshot_list()),
])
def url(
    request,  # noqa: ANN001
    tmp_path,  # noqa: ANN001
) -> str:
    scheme, user_information, snapshot_list = request.param
    path = tmp_path / "sample.mind"
    with path.open(mode="wb") as file:
        file.write(user_information)
        file.write(snapshot_list)
    return furl().set(scheme=scheme, path=str(path))


@pytest.fixture
def reader(url: str) -> Reader:
    return Reader(url=str(url))


def test_user_information(reader: Reader):
    assert reader.user_information.id == ID  # Property.
    assert reader.user_information.username == NAME  # Property.
    assert reader.user_information.birthday == BIRTHDAY
    assert reader.user_information.gender == GENDER


def test_reader_as_snapshot_generator(reader: Reader):
    reader_iterator = iter(reader)
    snapshot = next(reader_iterator)
    assert isinstance(snapshot, Snapshot)
    snapshot = next(reader_iterator)
    assert isinstance(snapshot, Snapshot)
    with pytest.raises(StopIteration):
        next(reader_iterator)
