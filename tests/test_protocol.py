import pytest

from src.protocol import Config, Hello


USER_ID = 1
USERNAME = "BarakB"
BIRTH_DAY = 3
GENDER = "m"
SERIALIZED = (
    b'\x01\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00BarakB\x03\x00\x00\x00m'
)

SUPPORTED_FIELDS = ["timestamp", "color_image"]


@pytest.fixture
def hello() -> Hello:
    return Hello(
        user_id=USER_ID, username=USERNAME, birth_day=BIRTH_DAY, gender=GENDER
    )


@pytest.fixture
def config() -> Config:
    return Config(supported_fields=SUPPORTED_FIELDS)


def test_hello_serde(hello: Hello):
    assert hello == Hello.deserialize(hello.serialize())


def test_config_serde(config: Config):
    assert config == Config.deserialize(config.serialize())
