
from __future__ import annotations

__all__ = ["Server"]

import socket as sockets
from contextlib import suppress
from threading import Lock, Thread

from . import Connection
from . import Address, FixedQueue, call


class Server:
    """
    Server that forms and controls connection and communication between
    itself and the client(s)

    self.clients: dict
    self.socket: socket.socket
    """
    address: Address
    socket: sockets.socket
    closed: bool = False
    clientLock: Lock
    clients: dict[Address, Connection]
    accpThread: Thread
    reqThread: Thread
    recvThreads: list[Thread]
    queue: FixedQueue[tuple[Address, dict]]

    def __init__(self, ip: Address, timeout: float=10., queueLength=1024):
        self.address = ip
        self.socket = sockets.socket()
        self.socket.bind(ip.astuple())
        self.socket.listen()
        self.socket.settimeout(timeout)
        self.clientLock = Lock()
        self.clients = {}
        self.queue = FixedQueue(queueLength)
        self.recvThreads = []
        self.accept_clients()

    def __str__(self) -> str:
        return str(self.queue)

    def __repr__(self) -> str:
        return f"Server at {self.address} has ({len(self.clients)} clients"

    def __str__(self) -> str:
        return repr(self)

    def __enter__(self):
        pass

    def __exit__(self, *ergs):
        self.close()

    def operate(self) -> Server:
        "opens a new thread constantly responding to requests"
        "<>.handle_request will be called with requests when they arrive"
        self.reqThread = call(lambda: self._operate())
        return self

    def accept_clients(self) -> Server:
        "opens a new thread constantly accepting new clients"
        self.accpThread = call(lambda: self._accept_clients())
        return self

    def _handle_request(self, addr: Address, data: dict):
        # empty packet means dead connection
        # this method removes dead connections
        if data is None:
            with self.clientLock:
                del self.clients[addr]
            return
        self.handle_request(addr, data)

    def handle_request(self, addr: Address, data: dict):
        raise NotImplementedError(f"Server `{self.__class__.__qualname__}` `{self.__class__}` is not set up to be a requests server")

    def send_all(self, data: dict):
        "sends given packet to every open Connection"
        with self.clientLock:
            for client in self.clients.values():
                client.send(data)

    def close(self):
        self.closed = True
        self.socket.close()
        self.flush()
        with self.clientLock:
            for conn in self.clients.values():
                with suppress(AttributeError):
                    conn.close()

    def flush(self):
        for cmd in iter(self.queue.dequeue, None):
            self._handle_request(*cmd)

    def _accept_clients(self):
        "constantly accept new clients and add them to the active client list"
        while not self.closed:
            try:
                conn = Connection(self.socket.accept(), self.queue)
                with self.clientLock:
                    self.clients[conn.addr] = conn
                t = call(lambda: conn.recv_repeat(self))
                self.recvThreads.append(t)
            except sockets.timeout:
                pass
            except OSError:
                pass

    def _operate(self):
        while not self.closed:
            cmd = self.queue.dequeue()
            if cmd is not None:
                self._handle_request(*cmd)
