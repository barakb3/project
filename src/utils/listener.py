import socket

from .connection import Connection


class Listener:
    def __init__(
            self,
            port: str,
            host: str = "0.0.0.0",
            backlog: int = 1000,
            reuseaddr: bool = True
    ):
        self.port = port
        self.host = host
        self.backlog = backlog
        self.reuseaddr = reuseaddr
        self.s = socket.socket()
        if reuseaddr:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

    def __repr__(self) -> str:
        return ((f"{self.__class__.__name__}(port={self.port}, "
                 f"host=\"{self.host}\", "
                 f" backlog={self.backlog}, "
                 f"reuseaddr={self.reuseaddr}"))

    def start(self):
        self.s.listen(self.backlog)

    def stop(self):
        self.s.close()

    def accept(self) -> Connection:
        client, address = self.s.accept()
        return Connection(conn=client)

    def __enter__(self) -> "Listener":
        self.start()
        return self

    def __exit__(self, exception, error, traceback):
        self.stop()
