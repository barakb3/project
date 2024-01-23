import json

from ..constants import DOUBLE_SIZE_IN_BYTES
from ..server import Context
from ..utils import from_bytes


def parse_translation(context: Context, translation_msg: bytes):
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
    context.save(
        file_rel_path="translation.json",
        content=json.dumps(
            {
                "x": translation[0],
                "y": translation[1],
                "z": translation[2],
            }
        )
    )


parse_translation.required_fields = ("translation", )
