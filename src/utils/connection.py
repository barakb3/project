import socket
import time


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

    def receive(self, size: int) -> bytes:
        msg = self.conn.recv(size)
        print(msg)
        # if len(msg) < size:
        #     raise Exception(f"Connection was closed \
        #                     before all data was received. {len(msg)} {size}")
        return msg

    def close(self):
        self.conn.close()

    def __enter__(self) -> "Connection":
        return self

    def __exit__(self, exception, error, traceback):
        self.close()

    def connect(host: str, port: int) -> "Connection":
        conn = socket.socket()
        time.sleep(0.1)  # Wait for server to start listening.
        conn.connect((host, port))
        return Connection(conn=conn)
