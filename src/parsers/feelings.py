import json

from ..server import Context


def parse_feelings(context: Context, feelings: tuple):
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
