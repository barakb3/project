from PIL import Image

from ..constants import BYTE_SIZE_IN_BYTES, UINT32_SIZE_IN_BYTES
from ..protocol import NUM_BYTES_PIXEL_COLOR_IMAGE
from ..server import Context
from ..utils import from_bytes


# Can also be a function like `parse_color_image` but here to demonstrate
# the concept of a parser that has a state that can be reflected in the class
# fields.
class ImageColorParser:
    required_fields = ("color_image", )

    # `self` isn't used since there is no need for any "state" changes.
    def parse(
        self, context: Context, color_image_msg: bytes
    ):
        msg_index = 0
        color_image_width = from_bytes(
            data=color_image_msg[
                msg_index:msg_index + UINT32_SIZE_IN_BYTES
            ],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        color_image_height = from_bytes(
            data=color_image_msg[
                msg_index:msg_index + UINT32_SIZE_IN_BYTES
            ],
            data_type="uint32",
            endianness="<",
        )
        msg_index += UINT32_SIZE_IN_BYTES
        color_image = []

        for _ in range(color_image_width * color_image_height):
            pixel = []
            for _ in range(NUM_BYTES_PIXEL_COLOR_IMAGE):
                pixel.append(
                    from_bytes(
                        data=color_image_msg[msg_index:msg_index + BYTE_SIZE_IN_BYTES],  # noqa: E501
                        data_type="byte",
                        endianness="<",
                    )
                )
                msg_index += BYTE_SIZE_IN_BYTES
            color_image.append(tuple(pixel))

        image = Image.new(
            "RGB",
            (color_image_width, color_image_height),
        )
        image.putdata(color_image)
        image.save(context.path("color_image.jpg"))
