import multiprocessing
import socket
import struct
# import subprocess
import time

import pytest


_SERVER_ADDRESS = "127.0.0.1", 5000
_SERVER_BACKLOG = 1000

_HEADER_FORMAT = "LLI"
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)

_USER_1 = 1
_USER_2 = 2
_THOUGHT_1 = "I'm hungry"
_THOUGHT_2 = "I'm sleepy"


@pytest.fixture
def get_message():  # noqa: ANN201
    parent, child = multiprocessing.Pipe()
    process = multiprocessing.Process(target=_run_server, args=(child,))
    process.start()
    parent.recv()
    try:
        def get_message():  # noqa: ANN201
            if not parent.poll(1):
                raise TimeoutError()
            return parent.recv()
        yield get_message
    finally:
        process.terminate()
        process.join()


# TODO: Add client tests.
# def test_connection(get_message):  # noqa: ANN001
#     host, port = _SERVER_ADDRESS
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_1}",
#             _THOUGHT_1,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     message = get_message()
#     assert message


# def test_user_id(get_message):  # noqa: ANN001
#     host, port = _SERVER_ADDRESS
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_1}",
#             _THOUGHT_1,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     assert user_id == _USER_1
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_2}",
#             _THOUGHT_1,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     assert user_id == _USER_2


# def test_timestamp(get_message):  # noqa: ANN001
#     host, port = _SERVER_ADDRESS
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_1}",
#             _THOUGHT_1,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     _assert_now(timestamp=timestamp)
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_2}",
#             _THOUGHT_2,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     _assert_now(timestamp=timestamp)


# def test_thought(get_message):  # noqa: ANN001
#     host, port = _SERVER_ADDRESS
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_1}",
#             _THOUGHT_1,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     assert thought == _THOUGHT_1
#     subprocess.Popen(
#         [
#             "python",
#             "-m",
#             "project",
#             "client",
#             "upload-thought",
#             f"{host}:{port}",
#             f"{_USER_1}",
#             _THOUGHT_2,
#         ],
#         stdout=subprocess.PIPE,
#     )
#     user_id, timestamp, thought = get_message()
#     assert thought == _THOUGHT_2


def _run_server(pipe):  # noqa: ANN001
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(_SERVER_ADDRESS)
    server.listen(_SERVER_BACKLOG)
    pipe.send("ready")
    with server:
        while True:
            connection, address = server.accept()
            _handle_connection(connection=connection, pipe=pipe)


def _handle_connection(connection: socket.socket, pipe):  # noqa: ANN001
    with connection:
        header_data = _receive_all(connection=connection, size=_HEADER_SIZE)
        user_id, timestamp, size = struct.unpack(_HEADER_FORMAT, header_data)
        data = _receive_all(connection=connection, size=size)
        thought = data.decode()
        pipe.send([user_id, timestamp, thought])


def _receive_all(connection: socket.socket, size: int) -> bytes:
    chunks = []
    while size > 0:
        chunk = connection.recv(size)
        if not chunk:
            raise RuntimeError("incomplete data")
        chunks.append(chunk)
        size -= len(chunk)
    return b"".join(chunks)


def _assert_now(timestamp: time.time):
    now = int(time.time())
    assert abs(now - timestamp) < 5
