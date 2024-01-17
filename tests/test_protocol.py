import pytest

from src.protocol import Hello


USER_ID = 1
USERNAME = "BarakB"
BIRTH_DAY = 3
GENDER = "m"
SERIALIZED = (
    b'\x01\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00BarakB\x03\x00\x00\x00m'
)


@pytest.fixture
def hello() -> Hello:
    return Hello(
        user_id=USER_ID, username=USERNAME, birth_day=BIRTH_DAY, gender=GENDER
    )


def test_hello_serialize_deserialize(hello: Hello):
    assert hello == Hello.deserialize(hello.serialize())
