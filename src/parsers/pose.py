import json

from ..constants import DOUBLE_SIZE_IN_BYTES
from ..server import Context
from ..utils import from_bytes


def parse_pose(context: Context, translation: tuple, rotation: tuple):
    context.path("./pose/").mkdir(parents=True, exist_ok=True)
    context.save(
        file_rel_path="./pose/translation.json",
        content=json.dumps(
            {
                "x": translation[0],
                "y": translation[1],
                "z": translation[2],
            }
        )
    )
    context.save(
        file_rel_path="./pose/rotation.json",
        content=json.dumps(
            {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2],
                "w": rotation[3],
            }
        )
    )


def deprecated_parse_pose(
    context: Context, translation_msg: bytes, rotation_msg: bytes
):
    context.path("./pose/").mkdir(parents=True, exist_ok=True)

    translation = []
    translation_msg_index = 0
    for _ in range(3):
        translation.append(
            from_bytes(
                data=translation_msg[
                    translation_msg_index:translation_msg_index + DOUBLE_SIZE_IN_BYTES  # noqa: E501
                ],
                data_type="double",
                endianness="<",
            )
        )
        translation_msg_index += DOUBLE_SIZE_IN_BYTES

    context.save(
        file_rel_path="./pose/translation.json",
        content=json.dumps(
            {
                "x": translation[0],
                "y": translation[1],
                "z": translation[2],
            }
        )
    )

    rotation = []
    rotation_msg_index = 0
    for _ in range(4):
        rotation.append(
            from_bytes(
                data=rotation_msg[
                    rotation_msg_index:rotation_msg_index + DOUBLE_SIZE_IN_BYTES  # noqa: E501
                ],
                data_type="double",
                endianness="<",
            )
        )
        rotation_msg_index += DOUBLE_SIZE_IN_BYTES

    context.save(
        file_rel_path="./pose/rotation.json",
        content=json.dumps(
            {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2],
                "w": rotation[3],
            }
        )
    )


parse_pose.required_fields = ("translation", "rotation")
