import json

from ..constants import FLOAT_SIZE_IN_BYTES
from ..server import Context
from ..utils import from_bytes


def parse_feelings(context: Context, feelings_msg: bytes):
    feelings = []
    feelings_msg_index = 0
    for _ in range(4):
        feelings.append(
            from_bytes(
                data=feelings_msg[
                    feelings_msg_index:feelings_msg_index + FLOAT_SIZE_IN_BYTES
                ],
                data_type="float",
                endianness="<",
            )
        )
        feelings_msg_index += FLOAT_SIZE_IN_BYTES

    context.save(
        file_rel_path="./feelings.json",
        content=json.dumps(
            {
                "hunger": feelings[0],
                "thirst": feelings[1],
                "exhaustion": feelings[2],
                "happiness": feelings[3],
            }
        )
    )


parse_feelings.required_fields = ("feelings", )
