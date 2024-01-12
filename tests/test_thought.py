import datetime as dt

import pytest

from src import Thought


user_id = 1
datetime = dt.datetime(2000, 1, 1, 10, 0, tzinfo=dt.timezone.utc)
thought = "I'm hungry"
serialized = (
    b"\x01\x00\x00\x00\x00\x00\x00\x00 \xd0m8\x00\x00\x00\x00\n\x00\x00\x00"
    b"I'm hungry"
)


@pytest.fixture
def t() -> Thought:
    return Thought(user_id=user_id, timestamp=datetime, thought=thought)


def test_attributes(t: Thought):
    assert t.user_id == user_id
    assert t.timestamp == datetime
    assert t.thought == thought


def test_repr(t: Thought):
    assert repr(t) == (
        f"Thought(user_id={user_id!r}, "
        f"timestamp={datetime!r}, thought={thought!r})"
    )


def test_str(t: Thought):
    assert str(t) == (
        f"[{datetime:%Y-%m-%d %H:%M:%S}] user {user_id}: {thought}"
    )


def test_eq(t: Thought):
    t1 = Thought(user_id=user_id, timestamp=datetime, thought=thought)
    assert t1 == t
    t2 = Thought(user_id=user_id + 1, timestamp=datetime, thought=thought)
    assert t2 != t
    t3 = Thought(
        user_id=user_id,
        timestamp=datetime + dt.timedelta(minutes=1),
        thought=thought
    )
    assert t3 != t
    t4 = Thought(user_id=user_id, timestamp=datetime, thought=thought + "!")
    assert t4 != t
    t5 = 1
    assert t5 != t
    t6: Thought = lambda: None
    t6.user_id = user_id
    t6.timestamp = datetime
    t6.thought = thought
    assert t6 != t


def test_serialize(t: Thought):
    assert t.serialize() == serialized


def test_deserialize(t: Thought):
    t = Thought.deserialize(data=serialized)
    assert t.user_id == user_id
    assert t.timestamp == datetime
    assert t.thought == thought


def test_symmetry(t: Thought):
    assert Thought.deserialize(data=t.serialize()) == t
