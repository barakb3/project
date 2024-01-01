import socket

from .connection import Connection


class Listener:
    def __init__(self, port, host='0.0.0.0', backlog=1000, reuseaddr=True):
        self.port = port
        self.host = host
        self.backlog = backlog
        self.reuseaddr = reuseaddr
        self.s = socket.socket()
        if reuseaddr:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

    def __repr__(self):
        return ((f'{self.__class__.__name__}(port={self.port}, '
                 f'host=\'{self.host}\', '
                 f' backlog={self.backlog}, '
                 f'reuseaddr={self.reuseaddr}'))

    def start(self):
        self.s.listen(self.backlog)

    def stop(self):
        self.s.close()

    def accept(self):
        client, address = self.s.accept()
        return Connection(client)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception, error, traceback):
        self.stop()
