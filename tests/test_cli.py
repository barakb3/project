import subprocess


def test_run_server():
    process = subprocess.Popen(
        ["python", "-m", "project", "server", "run-server"],
        stderr=subprocess.PIPE,
    )
    _, stderr = process.communicate()
    assert b"missing argument" in stderr.lower()


def test_run_webserver():
    process = subprocess.Popen(
        ["python", "-m", "project", "server", "run-webserver"],
        stderr=subprocess.PIPE,
    )
    _, stderr = process.communicate()
    assert b"missing argument" in stderr.lower()


def test_reader():
    process = subprocess.Popen(
        ["python", "-m", "project", "client", "read"],
        stderr=subprocess.PIPE,
    )
    _, stderr = process.communicate()
    assert b"missing argument" in stderr.lower()


# @contextlib.contextmanager
# def _argv(*args):
#     command = lambda: None
#     command.exit_code = 0
#     try:
#         argv = sys.argv[1:]
#         sys.argv[1:] = args
#         yield command
#     except SystemExit as e:
#         command.exit_code = e.args[0] if e.args else 0
#     finally:
#         sys.argv[1:] = argv
