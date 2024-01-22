import pytest

from src.protocol import (
    Config,
    EMPTY_COLOR_IMAGE,
    EMPTY_DEPTH_IMAGE,
    EMPTY_DIM,
    EMPTY_FEELINGS,
    EMPTY_ROTATION,
    EMPTY_TRANSLATION,
    Hello,
    Snapshot,
)

# Snapshot 1.
TIMESTAMP_1 = 1000
TRANSLATION_1 = (1.1, 1.2, 1.3)
ROTATION_1 = (1.1, 1.2, 1.3, 1.4)
COLOR_IMAGE_WIDTH_1 = 2
COLOR_IMAGE_HEIGHT_1 = 2
COLOR_IMAGE_1 = b"\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00"
DEPTH_IMAGE_WIDTH_1 = 2
DEPTH_IMAGE_HEIGHT_1 = 2
DEPTH_IMAGE_1 = [1.0, 1.0, 1.0, 1.0]
FEELINGS_1 = (1.1, 1.2, 1.3, 1.4)

# Snapshot 2.
TIMESTAMP_2 = 2000
TRANSLATION_2 = (2.1, 2.2, 2.3)
ROTATION_2 = (2.1, 2.2, 2.3, 2.4)
COLOR_IMAGE_WIDTH_2 = 2
COLOR_IMAGE_HEIGHT_2 = 3
COLOR_IMAGE_2 = b"\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00"  # noqa: E501
DEPTH_IMAGE_WIDTH_2 = 2
DEPTH_IMAGE_HEIGHT_2 = 3
DEPTH_IMAGE_2 = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
FEELINGS_2 = (2.1, 2.2, 2.3, 2.4)

USER_ID = 1
USERNAME = "BarakB"
BIRTHDAY = 3
GENDER = "m"

SUPPORTED_FIELDS = ("translation", "color_image")


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


def test_hello_serde(hello: Hello):
    assert hello == Hello.deserialize(hello.serialize())


def test_config_serde(config: Config):
    assert config == Config.deserialize(config.serialize())


def test_snapshot_eq(snapshot: Snapshot):
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


def test_supported_fields(snapshot: Snapshot):
    supported_snapshot = snapshot.clone_by_supported_fields(
        supported_fields=SUPPORTED_FIELDS
    )
    if "translation" in SUPPORTED_FIELDS:
        translation = TRANSLATION_1
    else:
        translation = EMPTY_TRANSLATION
    if "rotation" in SUPPORTED_FIELDS:
        rotation = ROTATION_1
    else:
        rotation = EMPTY_ROTATION
    if "color_image" in SUPPORTED_FIELDS:
        color_image_width = COLOR_IMAGE_WIDTH_1
        color_image_height = COLOR_IMAGE_HEIGHT_1
        color_image = COLOR_IMAGE_1
    else:
        color_image_width = EMPTY_DIM
        color_image_height = EMPTY_DIM
        color_image = EMPTY_COLOR_IMAGE
    if "depth_image" in SUPPORTED_FIELDS:
        depth_image_width = DEPTH_IMAGE_WIDTH_1
        depth_image_height = DEPTH_IMAGE_HEIGHT_1
        depth_image = DEPTH_IMAGE_1
    else:
        depth_image_width = EMPTY_DIM
        depth_image_height = EMPTY_DIM
        depth_image = EMPTY_DEPTH_IMAGE
    if "feelings" in SUPPORTED_FIELDS:
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
    assert supported_snapshot == expected
