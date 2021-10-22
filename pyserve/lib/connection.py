
from __future__ import annotations

__all__ = ["Connection"]

from . import Queue, Network


class Connection:
    "A server-sided connection to a specific client"
    def __init__(self, connect, queue: Queue, timeout: float = 10.):
        self.closed = False
        self.conn, self.addr = connect
        self.queue = queue
        self.timeout = timeout

    def __del__(self):
        self.close()

    def send(self, data: dict) -> bool:
        "send data over <conn>"
        if self.closed:
            return False
        Network.msgsend(self.conn, data)
        return True

    def close(self):
        self.closed = True
        self.conn.close()

    def recv(self) -> bool:
        "returns success flag. data stored in the Connection's queue"
        # error checking to make sure the connection is still open
        if self.closed:
            return False
        try:
            data = Network.msgrecv(self.conn, self.timeout)
        except (ConnectionAbortedError, ConnectionResetError, OSError):
            self.queue.enqueue((self.addr, None))
            return False
        # actually got a packet: checking if real
        if data is None:
            self.queue.enqueue((self.addr, None))
            return False
        self.queue.enqueue((self.addr, data))
        return True

    def recv_repeat(self, server):
        "recv but until connection closed. thread always listening"
        while not (self.closed) and not (server.closed):
            if not self.recv():
                self.close()
                return
