import click
from pathlib import Path
import signal
import threading

from src.thought import Thought
from src.utils import Listener


class Handler(threading.Thread):
    def __init__(self, client, data_dir, lock):
        super().__init__()
        self.client = client
        self.data_dir_path = Path(data_dir)
        self.lock = lock
        self.msg = None
        self.thought = None

    def run(self):
        msg = self.read_message()
        if len(msg) < 20:
            raise Exception("Incomplete meta data received.")
        self.thought = Thought.deserialize(msg)
        self.lock.acquire()
        self.write_thought()
        self.lock.release()
        self.client.close()

    def read_message(self):
        msg = bytearray(self.client.receive(1024))
        while (cont_msg := self.client.receive(1024)):
            msg += cont_msg
        return msg

    def validate_message(self):
        if len(self.msg) < 20:
            raise Exception("Incomplete meta data received.")

    def write_thought(self):
        dir_path = self.data_dir_path / f"{self.thought.user_id}"
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = \
            dir_path / f"{self.thought.timestamp:%Y-%m-%d_%H-%M-%S}.txt"
        file_path.touch()
        with file_path.open(mode="r+") as f:
            if f.read() == "":
                f.write(f"{self.thought.thought}")
            else:
                f.write(f"\n{self.thought.thought}")


@click.command()
@click.argument("address")
@click.argument("data_dir")
def run_server(address, data_dir):
    ip, port = address.split(":", 1)
    signal.SIGINT
    with Listener(port=int(port), host=ip) as listener:
        lock = threading.Lock()
        while True:
            client = listener.accept()
            newthread = Handler(client, data_dir, lock)
            newthread.start()
