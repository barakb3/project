import pathlib
import signal
import socket
import subprocess
import threading
import time

import pytest


_SERVER_ADDRESS = "127.0.0.1", 5000
_DATA_DIR_PATH = pathlib.Path(__file__).absolute().parent / "tests" / "data"


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
