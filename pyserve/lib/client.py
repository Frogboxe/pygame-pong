
__all__ = ["Client"]

from . import Address, Network
import socket as sockets

class Client:
    "simple connection handler for a client connecting to a server"
    def __init__(self, ip: Address, timeout: float = 10.):
        self.socket = sockets.socket()
        self.closed = False
        self.ip = ip
        self.timeout = timeout
        self.connect()

    def __del__(self):
        self.close()

    def connect(self):
        self.socket.connect(self.ip.astuple())

    def request(self, data: dict) -> dict:
        self.send(data)
        return self.recv()

    def send(self, data: dict):
        Network.msgsend(self.socket, data)

    def recv(self) -> dict:
        data = None
        while data is None:
            try:
                data = Network.msgrecv(self.socket, self.timeout)
            except (ConnectionAbortedError, ConnectionResetError):
                pass
        return data

    def close(self):
        self.socket.close()
