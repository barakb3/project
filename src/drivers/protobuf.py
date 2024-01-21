from collections import namedtuple


class ProtobufDriver:
    def __init__(self):
        pass

    def get_user_information(self) -> tuple:
        user_information = namedtuple(
            "user_information", ["id", "username", "birthday", "gender"]
        )
        return user_information

    def get_snapshot(self):
        pass
