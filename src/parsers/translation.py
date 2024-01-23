import json
from pathlib import Path

from ..constants import DOUBLE_SIZE_IN_BYTES
from ..utils import from_bytes


def parse_translation(snapshot_dir_path: Path, translation_msg: bytes):
    translation = []
    msg_index = 0
    for _ in range(3):
        translation.append(
            from_bytes(
                data=translation_msg[
                    msg_index:msg_index + DOUBLE_SIZE_IN_BYTES
                ],
                data_type="double",
                endianness="<",
            )
        )
        msg_index += DOUBLE_SIZE_IN_BYTES
    with open(snapshot_dir_path / "translation.json", "w") as writer:
        json.dump(
            {
                "x": translation[0],
                "y": translation[1],
                "z": translation[2],
            },
            writer
        )


parse_translation.required_fields = ("translation", )
