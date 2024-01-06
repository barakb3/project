import datetime as dt
import struct


class Thought:
    """
    A class representing a thought.
    """
    def __init__(self, user_id: str, timestamp: dt.datetime, thought: str):
        self.user_id = user_id
        self.timestamp = timestamp
        self.thought = thought

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(user_id={self.user_id!r}, "
            f"timestamp={self.timestamp!r}, "
            f"thought={self.thought!r})"
        )

    def __str__(self) -> str:
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] "
            f"user {self.user_id}: {self.thought}"
        )

    def __eq__(self, other: "Thought") -> bool:
        if not isinstance(other, Thought):
            return NotImplemented
        return self.user_id == other.user_id and \
            self.timestamp == other.timestamp and \
            self.thought == other.thought

    def serialize(self) -> bytes:
        encoded_thought = bytes(self.thought, "utf-8")
        return struct.pack(
            "<QQI{}s".format(len(encoded_thought)),
            int(self.user_id),
            int(self.timestamp.timestamp()),
            len(encoded_thought),
            encoded_thought,
        )

    def deserialize(data: bytes) -> "Thought":
        user_id = struct.unpack("<Q", data[:8])[0]
        timestamp = struct.unpack("<Q", data[8:16])[0]
        thought_len = struct.unpack("<I", data[16:20])[0]
        if len(data) - thought_len != 20:
            raise Exception("Message length received doesn't match.")
        thought = struct.unpack(
            "<{}s".format(thought_len),
            data[20:],
        )[0].decode("utf-8")
        return Thought(
            user_id=user_id,
            timestamp=dt.datetime.fromtimestamp(
                timestamp,
                tz=dt.timezone.utc,
            ),
            thought=thought,
        )
