import struct
from urllib.parse import urlunparse

import pytest

from src.protocol import Snapshot
from src.reader import Reader

# Snapshot 1.
BINARY_TIMESTAMP_1 = b"\xe8\x03\x00\x00\x00\x00\x00\x00"
BINARY_TRANSLATION_1 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
BINARY_ROTATION_1 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
BINARY_COLOR_IMAGE_HEIGHT_1 = b"\x00\x00\x00\x00"
BINARY_COLOR_IMAGE_WIDTH_1 = b"\x00\x00\x00\x00"
BINARY_COLOR_IMAGE_1 = b""
BINARY_DEPTH_IMAGE_HEIGHT_1 = b"\x00\x00\x00\x00"
BINARY_DEPTH_IMAGE_WIDTH_1 = b"\x00\x00\x00\x00"
BINARY_DEPTH_IMAGE_1 = b""
BINARY_FEELINGS_1 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501

# Snapshot 2.
BINARY_TIMESTAMP_2 = b"\xd0\x07\x00\x00\x00\x00\x00\x00"
BINARY_TRANSLATION_2 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
BINARY_ROTATION_2 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501
BINARY_COLOR_IMAGE_HEIGHT_2 = b"\x00\x00\x00\x00"
BINARY_COLOR_IMAGE_WIDTH_2 = b"\x00\x00\x00\x00"
BINARY_COLOR_IMAGE_2 = b""
BINARY_DEPTH_IMAGE_HEIGHT_2 = b"\x00\x00\x00\x00"
BINARY_DEPTH_IMAGE_WIDTH_2 = b"\x00\x00\x00\x00"
BINARY_DEPTH_IMAGE_2 = b""
BINARY_FEELINGS_2 = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # noqa: E501


ID = 3
NAME = "Barak Basson"
BIRTHDAY = 699746400
GENDER = "m"


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
    return BINARY_TIMESTAMP_1 + \
        BINARY_TRANSLATION_1 + \
        BINARY_ROTATION_1 + \
        BINARY_COLOR_IMAGE_HEIGHT_1 + \
        BINARY_COLOR_IMAGE_WIDTH_1 + \
        BINARY_COLOR_IMAGE_1 + \
        BINARY_DEPTH_IMAGE_HEIGHT_1 + \
        BINARY_DEPTH_IMAGE_WIDTH_1 + \
        BINARY_DEPTH_IMAGE_1 + \
        BINARY_FEELINGS_1 + \
        BINARY_TIMESTAMP_2 + \
        BINARY_TRANSLATION_2 + \
        BINARY_ROTATION_2 + \
        BINARY_COLOR_IMAGE_HEIGHT_2 + \
        BINARY_COLOR_IMAGE_WIDTH_2 + \
        BINARY_COLOR_IMAGE_2 + \
        BINARY_DEPTH_IMAGE_HEIGHT_2 + \
        BINARY_DEPTH_IMAGE_WIDTH_2 + \
        BINARY_DEPTH_IMAGE_2 + \
        BINARY_FEELINGS_2


@pytest.fixture
def path(
    tmp_path, metadata: bytes, snapshot_list: bytes  # noqa: ANN001
) -> str:
    sample_path = tmp_path / "sample.mind"
    with sample_path.open(mode="wb") as file:
        file.write(metadata)
        file.write(snapshot_list)
    return sample_path


@pytest.fixture
def url(
    path: str,
    scheme: str = "binary",
    netloc: str = "",
    params: str = "",
    query: str = "",
    fragment: str = "",
) -> str:
    return urlunparse(
        components=(scheme, netloc, str(path), params, query, fragment)
    )


@pytest.fixture
def reader(url: str) -> Reader:
    return Reader(url=url)


def test_metadata(reader: Reader):
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
