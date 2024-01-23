import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from ..constants import FLOAT_SIZE_IN_BYTES, UINT32_SIZE_IN_BYTES
from ..server import Context
from ..utils import from_bytes


matplotlib.use('Agg')


def parse_depth_image(context: Context, depth_image_msg: bytes):
    msg_index = 0
    depth_image_width = from_bytes(
        data=depth_image_msg[
            msg_index:msg_index + UINT32_SIZE_IN_BYTES
        ],
        data_type="uint32",
        endianness="<",
    )
    msg_index += UINT32_SIZE_IN_BYTES
    depth_image_height = from_bytes(
        data=depth_image_msg[
            msg_index:msg_index + UINT32_SIZE_IN_BYTES
        ],
        data_type="uint32",
        endianness="<",
    )
    msg_index += UINT32_SIZE_IN_BYTES
    depth_image = []

    for _ in range(depth_image_width * depth_image_height):
        depth_image.append(
            from_bytes(
                data=depth_image_msg[msg_index:msg_index + FLOAT_SIZE_IN_BYTES],  # noqa: E501
                data_type="float",
                endianness="<",
            )
        )
        msg_index += FLOAT_SIZE_IN_BYTES

    plt.imshow(
        np.reshape(
            np.array(depth_image),
            newshape=(depth_image_height, depth_image_width),
        )
    )
    plt.savefig(
        context.path(file_rel_path="depth_image.png"), format="png"
    )


parse_depth_image.required_fields = ("depth_image", )
