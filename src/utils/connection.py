import socket
import time
import traceback

from ..constants import UINT32_SIZE_IN_BYTES
from ..protocol import from_bytes, to_bytes

CHUNK_SIZE_IN_BYTES = 2 ** 12


class Connection:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.ip, self.port = self.conn.getsockname()
        self.peer_ip, self.peer_port = self.conn.getpeername()

    def __repr__(self) -> str:
        return ((f"<Connection from {self.ip}:{self.port} "
                 f"to {self.peer_ip}:{self.peer_port}>"))

    def send(self, data: bytes):
        self.conn.sendall(data)

    def send_message(self, msg: bytes):
        size_prefixed_msg = to_bytes(
            value=len(msg), data_type="uint32", endianness="<"
        ) + msg
        for i in range(0, len(size_prefixed_msg), CHUNK_SIZE_IN_BYTES):
            chunk = size_prefixed_msg[i:i + CHUNK_SIZE_IN_BYTES]
            self.conn.sendall(chunk)

    def receive_message(self) -> bytes:
        msg_length = from_bytes(
            data=self.conn.recv(UINT32_SIZE_IN_BYTES),
            data_type="uint32",
            endianness="<",
        )
        msg = bytearray()
        for _ in range(0, msg_length, CHUNK_SIZE_IN_BYTES):
            msg += self.conn.recv(CHUNK_SIZE_IN_BYTES)

        if len(msg) < msg_length:
            # Wait one second and try last time to receive all data.
            time.sleep(1)
            msg += self.conn.recv(CHUNK_SIZE_IN_BYTES)
            if len(msg) < msg_length:
                raise Exception(
                    "Connection was closed before all data was received."
                )
        return msg

    def close(self):
        self.conn.close()

    def __enter__(self) -> "Connection":
        return self

    def __exit__(
            self,
            exception: Exception,
            error: TypeError,
            traceback: traceback.TracebackException,
    ):
        self.close()

    def connect(host: str, port: int) -> "Connection":
        conn = socket.socket()
        time.sleep(0.1)  # Wait for server to start listening.
        conn.connect((host, port))
        return Connection(conn=conn)
