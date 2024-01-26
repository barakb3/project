import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from ..server import Context


matplotlib.use('Agg')


def parse_depth_image(
    context: Context,
    depth_image_width: int,
    depth_image_height: int,
    depth_image: tuple,
):
    if depth_image == tuple():
        return

    plt.imshow(
        np.reshape(
            np.array(depth_image),
            newshape=(depth_image_height, depth_image_width),
        )
    )
    plt.savefig(
        context.path(rel_path="depth_image.png"), format="png"
    )


parse_depth_image.required_fields = (
    "depth_image_width", "depth_image_height", "depth_image"
)
