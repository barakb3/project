import socket
import time

import pytest

from src.utils import Connection


_PORT = 5000


@pytest.fixture
def server():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", _PORT))
    server.listen(1000)
    try:
        time.sleep(0.1)
        yield server
    finally:
        server.close()


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
