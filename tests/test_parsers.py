import json
from pathlib import Path

from PIL import Image

import pytest

from src import parsers
from src.server import Context

from .test_utils import TIMESTAMP, USER_ID


@pytest.fixture
def context(tmp_path) -> Context:  # noqa: ANN001
    return Context(
        user_id=USER_ID,
        data_dir_path=str(tmp_path),
        timestamp=TIMESTAMP
    )


@pytest.fixture
def snapshot_dir_path(tmp_path, context: Context) -> Path:  # noqa: ANN001
    return (
        tmp_path / f"{context.user_id}" / f"{context.datetime:%Y-%m-%d_%H-%M-%S-%f}"  # noqa: E501
    )


@pytest.mark.parametrize(
    "translation, rotation",
    [
        ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)),
        ((1.0, 2.2, -1.1), (1.0, 0.2, 3.9, -2.0)),
    ],
)
def test_parse_pose(
    context: Context,
    snapshot_dir_path: Path,
    translation: tuple,
    rotation: tuple,
):
    expected_translation = {
        "x": translation[0],
        "y": translation[1],
        "z": translation[2],
    }
    expected_rotation = {
        "x": rotation[0],
        "y": rotation[1],
        "z": rotation[2],
        "w": rotation[3],
    }
    parsers.parse_pose(
        context=context, translation=translation, rotation=rotation
    )
    with open(snapshot_dir_path / "pose" / "translation.json", "r") as file:
        assert json.load(file) == expected_translation
    with open(snapshot_dir_path / "pose" / "rotation.json", "r") as file:
        assert json.load(file) == expected_rotation


@pytest.mark.parametrize(
    "color_image_width, color_image_height, color_image",
    [
        (0, 0, b""),
        (2, 2, b"\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00"),
    ],
)
def test_parse_color_image(
    context: Context,
    snapshot_dir_path: Path,
    color_image_width: int,
    color_image_height: int,
    color_image: bytes,
):
    image_color_parser = parsers.ImageColorParser()
    image_color_parser.parse(
        context=context,
        color_image_width=color_image_width,
        color_image_height=color_image_height,
        color_image=color_image,
    )
    if color_image != b"":
        assert Path.is_file(snapshot_dir_path / "color_image.jpg")
        assert (
            Image.open(snapshot_dir_path / "color_image.jpg").format == "JPEG"
        )


@pytest.mark.parametrize(
    "depth_image_width, depth_image_height, depth_image",
    [
        (0, 0, tuple()),
        (2, 2, (0.05, -0.02, 0.003, 1.0)),
    ],
)
def test_parse_depth_image(
    context: Context,
    snapshot_dir_path: Path,
    depth_image_width: int,
    depth_image_height: int,
    depth_image: tuple,
):
    parsers.parse_depth_image(
        context=context,
        depth_image_width=depth_image_width,
        depth_image_height=depth_image_height,
        depth_image=depth_image,
    )
    if depth_image != tuple():
        assert Path.is_file(snapshot_dir_path / "depth_image.png")
        assert (
            Image.open(snapshot_dir_path / "depth_image.png").format == "PNG"
        )


@pytest.mark.parametrize(
    "feelings",
    [
        ((0.0, 0.0, 0.0, 0.0)),
    ],
)
def test_parse_feelings(
    context: Context, snapshot_dir_path: Path, feelings: tuple
):
    expected_feelings = {
        "hunger": feelings[0],
        "thirst": feelings[1],
        "exhaustion": feelings[2],
        "happiness": feelings[3],
    }
    parsers.parse_feelings(context=context, feelings=feelings)
    with open(snapshot_dir_path / "feelings.json", "r") as file:
        assert json.load(file) == expected_feelings
