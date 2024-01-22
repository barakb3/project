import pytest

from src.protocol import (
    CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT,
    Config,
    EMPTY_BINARY_COLOR_IMAGE,
    EMPTY_BINARY_DEPTH_IMAGE,
    EMPTY_BINARY_FEELINGS,
    EMPTY_BINARY_ROTATION,
    EMPTY_BINARY_TRANSLATION,
    Hello,
    Snapshot,
    SnapshotBinaryBlob,
    SnapshotMetadata,
)

from .test_utils import (  # noqa: I101
    BINARY_TIMESTAMP_1,
    BINARY_TRANSLATION_1,
    BINARY_ROTATION_1,
    BINARY_COLOR_IMAGE_HEIGHT_1,
    BINARY_COLOR_IMAGE_WIDTH_1,
    BINARY_COLOR_IMAGE_1,
    BINARY_DEPTH_IMAGE_HEIGHT_1,
    BINARY_DEPTH_IMAGE_WIDTH_1,
    BINARY_DEPTH_IMAGE_1,
    BINARY_FEELINGS_1,
    TIMESTAMP_1,
    COLOR_IMAGE_WIDTH_1,
    COLOR_IMAGE_HEIGHT_1,
    DEPTH_IMAGE_WIDTH_1,
    DEPTH_IMAGE_HEIGHT_1,
    BINARY_TIMESTAMP_2,
    BINARY_TRANSLATION_2,
    BINARY_ROTATION_2,
    BINARY_COLOR_IMAGE_HEIGHT_2,
    BINARY_COLOR_IMAGE_WIDTH_2,
    BINARY_COLOR_IMAGE_2,
    BINARY_DEPTH_IMAGE_HEIGHT_2,
    BINARY_DEPTH_IMAGE_WIDTH_2,
    BINARY_DEPTH_IMAGE_2,
    BINARY_FEELINGS_2,
    TIMESTAMP_2,
    COLOR_IMAGE_WIDTH_2,
    COLOR_IMAGE_HEIGHT_2,
    DEPTH_IMAGE_WIDTH_2,
    DEPTH_IMAGE_HEIGHT_2
)

USER_ID = 1
USERNAME = "BarakB"
BIRTHDAY = 3
GENDER = "m"

SUPPORTED_FIELDS = ["translation", "color_image"]


@pytest.fixture
def hello() -> Hello:
    return Hello(
        user_id=USER_ID, username=USERNAME, birthday=BIRTHDAY, gender=GENDER
    )


@pytest.fixture
def config() -> Config:
    return Config(supported_fields=SUPPORTED_FIELDS)


@pytest.fixture
def snapshot() -> Snapshot:
    return Snapshot(
        binary_blob=SnapshotBinaryBlob(
            timestamp=BINARY_TIMESTAMP_1,
            translation=BINARY_TRANSLATION_1,
            rotation=BINARY_ROTATION_1,
            color_image_width=BINARY_COLOR_IMAGE_WIDTH_1,
            color_image_height=BINARY_COLOR_IMAGE_HEIGHT_1,
            color_image=BINARY_COLOR_IMAGE_1,
            depth_image_width=BINARY_DEPTH_IMAGE_WIDTH_1,
            depth_image_height=BINARY_DEPTH_IMAGE_HEIGHT_1,
            depth_image=BINARY_DEPTH_IMAGE_1,
            feelings=BINARY_FEELINGS_1,
        ),
        metadata=SnapshotMetadata(
            timestamp=TIMESTAMP_1,
            color_image_width=COLOR_IMAGE_WIDTH_1,
            color_image_height=COLOR_IMAGE_HEIGHT_1,
            depth_image_width=DEPTH_IMAGE_WIDTH_1,
            depth_image_height=DEPTH_IMAGE_HEIGHT_1
        ),
    )


def test_hello_serde(hello: Hello):
    assert hello == Hello.deserialize(hello.serialize())


def test_config_serde(config: Config):
    assert config == Config.deserialize(config.serialize())


def test_snapshot_length(snapshot: Snapshot):
    assert len(snapshot) == CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT  # noqa: E501


def test_snapshot_eq(snapshot: Snapshot):
    other_snapshot = Snapshot(
        binary_blob=SnapshotBinaryBlob(
            timestamp=BINARY_TIMESTAMP_2,
            translation=BINARY_TRANSLATION_2,
            rotation=BINARY_ROTATION_2,
            color_image_width=BINARY_COLOR_IMAGE_WIDTH_2,
            color_image_height=BINARY_COLOR_IMAGE_HEIGHT_2,
            color_image=BINARY_COLOR_IMAGE_2,
            depth_image_width=BINARY_DEPTH_IMAGE_WIDTH_2,
            depth_image_height=BINARY_DEPTH_IMAGE_HEIGHT_2,
            depth_image=BINARY_DEPTH_IMAGE_2,
            feelings=BINARY_FEELINGS_2,
        ),
        metadata=SnapshotMetadata(
            timestamp=TIMESTAMP_2,
            color_image_width=COLOR_IMAGE_WIDTH_2,
            color_image_height=COLOR_IMAGE_HEIGHT_2,
            depth_image_width=DEPTH_IMAGE_WIDTH_2,
            depth_image_height=DEPTH_IMAGE_HEIGHT_2
        ),
    )
    assert snapshot != other_snapshot


def test_snapshot_timestamp(snapshot: Snapshot):
    assert snapshot.timestamp == "1970-01-01_00-00-01-000000"


def test_get_supported_fields(snapshot: Snapshot):
    supported_fields_msg = snapshot.get_supported_fields_msg(
        supported_fields=SUPPORTED_FIELDS
    )
    expected = bytearray(BINARY_TIMESTAMP_1)
    if "translation" in SUPPORTED_FIELDS:
        expected.extend(BINARY_TRANSLATION_1)
    else:
        expected.extend(EMPTY_BINARY_TRANSLATION)
    if "rotation" in SUPPORTED_FIELDS:
        expected.extend(BINARY_ROTATION_1)
    else:
        expected.extend(EMPTY_BINARY_ROTATION)
    if "color_image" in SUPPORTED_FIELDS:
        expected.extend(
            BINARY_COLOR_IMAGE_WIDTH_1 + BINARY_COLOR_IMAGE_HEIGHT_1 + BINARY_COLOR_IMAGE_1  # noqa: E501
        )
    else:
        expected.extend(EMPTY_BINARY_COLOR_IMAGE)
    if "depth_image" in SUPPORTED_FIELDS:
        expected.extend(
            BINARY_DEPTH_IMAGE_WIDTH_1 + BINARY_DEPTH_IMAGE_HEIGHT_1 + BINARY_DEPTH_IMAGE_1  # noqa: E501
        )
    else:
        expected.extend(EMPTY_BINARY_DEPTH_IMAGE)
    if "feelings" in SUPPORTED_FIELDS:
        expected.extend(BINARY_FEELINGS_1)
    else:
        expected.extend(EMPTY_BINARY_FEELINGS)
    assert supported_fields_msg == expected
