import json

from ..server import Context


def parse_pose(context: Context, translation: tuple, rotation: tuple):
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


parse_pose.required_fields = ("translation", "rotation")
