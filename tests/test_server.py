import inspect
import signal
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

from src import parsers
from src.server import Context, load_parsers

from .test_utils import TIMESTAMP, USER_ID


_SERVER_ADDRESS = "127.0.0.1", 5000
_DATA_DIR_PATH = Path(__file__).absolute().parent / "tests" / "data"


@pytest.fixture
def server_process() -> subprocess.Popen:
    host, port = _SERVER_ADDRESS
    process = subprocess.Popen(
        [
            "python",
            "-m",
            "project",
            "server",
            "run-server",
            f"{host}:{port}",
            _DATA_DIR_PATH,
        ],
        stdout=subprocess.PIPE,
    )
    return process


def test_context(tmp_path):  # noqa: ANN001
    context = Context(
        user_id=USER_ID,
        data_dir_path=str(tmp_path),
        timestamp=TIMESTAMP
    )
    snapshot_dir_path = context.snapshot_dir_path

    assert context.path(
        rel_path="some/rel/path"
    ) == snapshot_dir_path / "some/rel/path"
    assert Path.is_dir(snapshot_dir_path)

    content = "Some content"
    context.save(file_rel_path="some/rel/path/file.txt", content=content)
    with open(snapshot_dir_path / "some/rel/path/file.txt", "r") as file:
        assert file.read() == content


def test_load_parsers():
    expected = {}
    for parser_name in parsers.__all__:
        parser = getattr(parsers, parser_name)
        if inspect.isfunction(parser):
            expected.update({parser.required_fields: parser})
        elif inspect.isclass(parser):
            obj = parser()
            expected.update({obj.required_fields: obj.parse})

    for required_fields, parser in load_parsers().items():
        assert required_fields in expected.keys()
        if inspect.ismethod(parser):
            assert parser.__func__ == expected[required_fields].__func__
        elif inspect.isfunction(parser):
            assert parser == expected[required_fields]
        else:
            assert False, "'parser' must be either a function or a method."


def test_connection(server_process: subprocess.Popen):
    thread = threading.Thread(target=server_process.communicate)
    thread.start()
    time.sleep(3)
    try:
        connection = socket.socket()
        connection.connect(_SERVER_ADDRESS)
        connection.close()
    finally:
        server_process.send_signal(signal.SIGINT)
        thread.join()
