import random
import struct

from project_pb2 import (
    ColorImage,
    DepthImage,
    Feelings,
    Pose,
    ProtoSnapshot,
)

import pytest

from src.snapshot import (
    EMPTY_COLOR_IMAGE,
    EMPTY_DEPTH_IMAGE,
    EMPTY_DIM,
    EMPTY_FEELINGS,
    EMPTY_ROTATION,
    EMPTY_TRANSLATION,
    Snapshot
)

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

REPR_REPRESENTATION = (
    "Snapshot(datetime=datetime.datetime(1970, 1, 1, 0, 0, 1, "
    "tzinfo=datetime.timezone.utc),\n"
    "translation={'x': 1.1, 'y': 1.2, 'z': 1.3},\n"
    "rotation={'x': 1.1, 'y': 1.2, 'z': 1.3, 'w': 1.4},\n"
    "color_image=<2x2>,\n"
    "depth_image=<2x2>,\n"
    "feelings={'hunger': 1.1, 'thirst': 1.2, 'exhaustion': 1.3, "
    "'happiness': 1.4})"
)
STR_REPRESENTATION = (
    "1970-01-01 00:00:01:000000, "
    "self.translation=(1.1, 1.2, 1.3), "
    "self.rotation=(1.1, 1.2, 1.3, 1.4), "
    "color_image=<2x2>, "
    "depth_image=<2x2>, "
    "self.feelings=(1.1, 1.2, 1.3, 1.4)"
)
ID = 3
NAME = "Barak Basson"
BIRTHDAY = 699746400


@pytest.fixture
def snapshot() -> Snapshot:
    return Snapshot(
        timestamp=TIMESTAMP_1,
        translation=TRANSLATION_1,
        rotation=ROTATION_1,
        color_image_width=COLOR_IMAGE_WIDTH_1,
        color_image_height=COLOR_IMAGE_HEIGHT_1,
        color_image=COLOR_IMAGE_1,
        depth_image_width=DEPTH_IMAGE_WIDTH_1,
        depth_image_height=DEPTH_IMAGE_HEIGHT_1,
        depth_image=DEPTH_IMAGE_1,
        feelings=FEELINGS_1,
    )


@pytest.fixture
def proto_snapshot() -> ProtoSnapshot:
    return ProtoSnapshot(
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


def test_repr(snapshot: Snapshot):
    assert repr(snapshot) == REPR_REPRESENTATION


def test_str(snapshot: Snapshot):
    assert str(snapshot) == STR_REPRESENTATION


def test_eq(snapshot: Snapshot):
    identical_snapshot = Snapshot(
        timestamp=TIMESTAMP_1,
        translation=TRANSLATION_1,
        rotation=ROTATION_1,
        color_image_width=COLOR_IMAGE_WIDTH_1,
        color_image_height=COLOR_IMAGE_HEIGHT_1,
        color_image=COLOR_IMAGE_1,
        depth_image_width=DEPTH_IMAGE_WIDTH_1,
        depth_image_height=DEPTH_IMAGE_HEIGHT_1,
        depth_image=DEPTH_IMAGE_1,
        feelings=FEELINGS_1,
    )
    assert snapshot == identical_snapshot

    other_snapshot = Snapshot(
        timestamp=TIMESTAMP_2,
        translation=TRANSLATION_2,
        rotation=ROTATION_2,
        color_image_width=COLOR_IMAGE_WIDTH_2,
        color_image_height=COLOR_IMAGE_HEIGHT_2,
        color_image=COLOR_IMAGE_2,
        depth_image_width=DEPTH_IMAGE_WIDTH_2,
        depth_image_height=DEPTH_IMAGE_HEIGHT_2,
        depth_image=DEPTH_IMAGE_2,
        feelings=FEELINGS_2,
    )
    assert snapshot != other_snapshot


def test_getitem(snapshot: Snapshot):
    assert snapshot["timestamp"] == TIMESTAMP_1


def test_serialize(snapshot: Snapshot, proto_snapshot: ProtoSnapshot):
    serialized = []
    serialized.append(struct.pack("<I", proto_snapshot.ByteSize()))
    serialized.append(proto_snapshot.SerializeToString())
    assert (
        snapshot.serialize() == b"".join(serialized)
    )


def test_clone_by_supported_fields(snapshot: Snapshot):
    fields = [
        "translation", "rotation", "color_image", "depth_image", "feelings"
    ]
    num_to_select = random.randint(1, len(fields))
    supported_fields = random.sample(fields, num_to_select)

    supported_snapshot = snapshot.clone_by_supported_fields(
        supported_fields=tuple(supported_fields)
    )
    if "translation" in supported_fields:
        translation = TRANSLATION_1
    else:
        translation = EMPTY_TRANSLATION
    if "rotation" in supported_fields:
        rotation = ROTATION_1
    else:
        rotation = EMPTY_ROTATION
    if "color_image" in supported_fields:
        color_image_width = COLOR_IMAGE_WIDTH_1
        color_image_height = COLOR_IMAGE_HEIGHT_1
        color_image = COLOR_IMAGE_1
    else:
        color_image_width = EMPTY_DIM
        color_image_height = EMPTY_DIM
        color_image = EMPTY_COLOR_IMAGE
    if "depth_image" in supported_fields:
        depth_image_width = DEPTH_IMAGE_WIDTH_1
        depth_image_height = DEPTH_IMAGE_HEIGHT_1
        depth_image = DEPTH_IMAGE_1
    else:
        depth_image_width = EMPTY_DIM
        depth_image_height = EMPTY_DIM
        depth_image = EMPTY_DEPTH_IMAGE
    if "feelings" in supported_fields:
        feelings = FEELINGS_1
    else:
        feelings = EMPTY_FEELINGS
    expected = Snapshot(
        timestamp=TIMESTAMP_1,
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
    assert (
        supported_snapshot == expected
    ), f"Supported fields in failure: {supported_fields}"


def test_from_parsed(snapshot: Snapshot, proto_snapshot: ProtoSnapshot):
    assert Snapshot.from_parsed(parsed=proto_snapshot) == snapshot
