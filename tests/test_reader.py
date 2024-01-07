import struct

import pytest

from src.utils.reader import (
    CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT,
    NUM_BYTES_PIXEL_COLOR_IMAGE,
    NUM_BYTES_PIXEL_DEPTH_IMAGE,
    Reader,
    Snapshot,
)

ID = 3
NAME = "Barak Basson"
BIRTHDAY = 699746400
GENDER = "m"

# Snapshot 1.
TIMESTAMP_SNAPSHOT = 1
TRANSLATION_X_SNAPSHOT = 1.1
TRANSLATION_Y_SNAPSHOT = 1.2
TRANSLATION_Z_SNAPSHOT = 1.3
ROTATION_X_SNAPSHOT = 1.11
ROTATION_Y_SNAPSHOT = 1.22
ROTATION_Z_SNAPSHOT = 1.33
ROTATION_W_SNAPSHOT = 1.44
COLOR_IMAGE_HEIGHT_SNAPSHOT = 1
COLOR_IMAGE_WIDTH_SNAPSHOT = 1
DEPTH_IMAGE_HEIGHT_SNAPSHOT = 1
DEPTH_IMAGE_WIDTH_SNAPSHOT = 1
HUNGER_SNAPSHOT = 1.111
THIRST_SNAPSHOT = 1.222
EXAUSTION_SNAPSHOT = 1.333
HAPPINESS_SNAPSHOT = 1.444


@pytest.fixture
def metadata() -> bytes:
    return struct.pack(
        "<QI{}sIc".format(len(NAME)),
        ID,
        len(NAME),
        bytes(NAME, "utf-8"),
        BIRTHDAY,
        bytes(GENDER, "utf-8"),
    )


@pytest.fixture
def snapshot_list() -> bytes:
    return struct.pack(
        "<QdddddddII{}BII{}fffff".format(
            NUM_BYTES_PIXEL_COLOR_IMAGE * COLOR_IMAGE_HEIGHT_SNAPSHOT * COLOR_IMAGE_WIDTH_SNAPSHOT, # noqa E501
            NUM_BYTES_PIXEL_DEPTH_IMAGE * DEPTH_IMAGE_HEIGHT_SNAPSHOT * DEPTH_IMAGE_WIDTH_SNAPSHOT, # noqa E501
        ),
        TIMESTAMP_SNAPSHOT,
        TRANSLATION_X_SNAPSHOT,
        TRANSLATION_Y_SNAPSHOT,
        TRANSLATION_Z_SNAPSHOT,
        ROTATION_X_SNAPSHOT,
        ROTATION_Y_SNAPSHOT,
        ROTATION_Z_SNAPSHOT,
        ROTATION_W_SNAPSHOT,
        COLOR_IMAGE_HEIGHT_SNAPSHOT,
        COLOR_IMAGE_WIDTH_SNAPSHOT,
        *[i for i in range(NUM_BYTES_PIXEL_COLOR_IMAGE * COLOR_IMAGE_HEIGHT_SNAPSHOT * COLOR_IMAGE_WIDTH_SNAPSHOT)], # noqa E501
        DEPTH_IMAGE_HEIGHT_SNAPSHOT,
        DEPTH_IMAGE_WIDTH_SNAPSHOT,
        *[float(i) for i in range(NUM_BYTES_PIXEL_DEPTH_IMAGE * DEPTH_IMAGE_HEIGHT_SNAPSHOT * DEPTH_IMAGE_WIDTH_SNAPSHOT)], # noqa E501
        HUNGER_SNAPSHOT,
        THIRST_SNAPSHOT,
        EXAUSTION_SNAPSHOT,
        HAPPINESS_SNAPSHOT,
    )


@pytest.fixture
def snapshot() -> Snapshot:
    return Snapshot(
        timestamp=TIMESTAMP_SNAPSHOT,
        color_image_width=COLOR_IMAGE_WIDTH_SNAPSHOT,
        color_image_height=COLOR_IMAGE_HEIGHT_SNAPSHOT,
        depth_image_width=DEPTH_IMAGE_WIDTH_SNAPSHOT,
        depth_image_height=DEPTH_IMAGE_HEIGHT_SNAPSHOT
    )


@pytest.fixture
def sample_path(tmp_path, metadata: bytes, snapshot_list: bytes) -> str: # noqa ANN001
    sample_path = tmp_path / "sample.mind"
    with sample_path.open(mode="wb") as file:
        file.write(metadata)
        file.write(snapshot_list)
    return sample_path


@pytest.fixture
def reader(sample_path: str) -> Reader:
    return Reader(path=sample_path)


def test_metadata(reader: Reader):
    assert reader.user_id == ID  # Property.
    assert reader.username == NAME  # Property.
    assert reader.birth_day == BIRTHDAY
    assert reader.gender == GENDER


def test_snapshot_as_a_generator(reader: Reader):
    reader_iterator = iter(reader)
    snapahot: Snapshot = next(reader_iterator)
    assert snapahot.timestamp == TIMESTAMP_SNAPSHOT
    assert snapahot.color_image_width == COLOR_IMAGE_WIDTH_SNAPSHOT
    assert snapahot.color_image_height == COLOR_IMAGE_HEIGHT_SNAPSHOT
    assert snapahot.depth_image_width == DEPTH_IMAGE_WIDTH_SNAPSHOT
    assert snapahot.depth_image_height == DEPTH_IMAGE_HEIGHT_SNAPSHOT


def test_snapshot_length(snapshot: Snapshot):
    assert len(snapshot) == CONSTANT_NUM_OF_BYTES_IN_SNAPSHOT + \
            (NUM_BYTES_PIXEL_COLOR_IMAGE * COLOR_IMAGE_WIDTH_SNAPSHOT * COLOR_IMAGE_HEIGHT_SNAPSHOT) + \
            (NUM_BYTES_PIXEL_DEPTH_IMAGE * DEPTH_IMAGE_WIDTH_SNAPSHOT * DEPTH_IMAGE_HEIGHT_SNAPSHOT) # noqa E501
