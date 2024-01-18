import socket
import struct
import time

import pytest

from src.utils import Connection

_SERVER_ADDRESS = "0.0.0.0"
_PORT = 5000

MSG = b"Hello, world!"
SIZE_PREFIXED_MSG = struct.pack("<I{}s".format(len(MSG)), len(MSG), MSG)


@pytest.fixture
def server():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((_SERVER_ADDRESS, _PORT))
    server.listen(1000)
    try:
        time.sleep(0.1)
        yield server
    finally:
        server.close()


class MockSocket:
    def __init__(self, data_sent: bytes):
        self.data_sent = data_sent
        self.data_index = 0

    def getsockname(self) -> tuple:
        return None, None

    def getpeername(self) -> tuple:
        return None, None

    def sendall(self, data: bytes):
        self.data_sent += data

    def recv(self, size: int) -> bytes:
        msg = self.data_sent[self.data_index:size]
        self.data_index += size
        return msg

    def get_data_sent(self) -> bytes:
        return self.data_sent


@pytest.fixture
def mock_socket(monkeypatch):  # noqa: ANN001
    def mock_socket(data_sent: bytes = b"") -> MockSocket:
        return MockSocket(data_sent=data_sent)
    monkeypatch.setattr(socket, "socket", mock_socket)


def test_context_manager(server: socket.socket):
    sock = socket.socket()
    sock.connect(("127.0.0.1", _PORT))
    connection = Connection(conn=sock)
    with connection:
        assert not sock._closed
    assert sock._closed


def test_connect(server: socket.socket):
    with Connection.connect(
        host="127.0.0.1", port=_PORT
    ) as connection:  # noqa: F841
        server.accept()


def test_send_message(mock_socket: MockSocket):
    conn: MockSocket = socket.socket()
    connection = Connection(conn=conn)
    connection.send_message(msg=MSG)
    assert conn.get_data_sent() == SIZE_PREFIXED_MSG


def test_receive_message(mock_socket: MockSocket):
    conn: MockSocket = socket.socket(data_sent=SIZE_PREFIXED_MSG)
    connection = Connection(conn=conn)
    assert connection.receive_message() == MSG

    conn: MockSocket = socket.socket(data_sent=SIZE_PREFIXED_MSG[:-1])
    connection = Connection(conn=conn)
    with pytest.raises(
        Exception,
        match="Connection was closed before all data was received."
    ):
        connection.receive_message()
