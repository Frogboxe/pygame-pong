
from __future__ import annotations

__all__ = ["Address", "call", "Network", "Queue", "FixedQueue"]

import json
import select
import socket as sockets
import struct
from collections.abc import Callable
from dataclasses import astuple, dataclass, field
from threading import Lock, Thread

import msgpack

INFO_BYTES = 4
BYTE_COUNT_ENCODING = ">L"

DENARY_MAX_LENGTH_DIGITS = 12
ENCODING = "utf-8"
ZERO_STRING = "0"

def call(func: Callable[..., None], **kwargs) -> Thread:
    "calls <func> in a subthread and returns that thread"
    "thread is a daemon by default"
    default = {
        "daemon": True
        }
    use = default | kwargs
    t = Thread(target=func, **use)
    t.start()
    return t

@dataclass(frozen=True)
class Address:
    addr: str=field(default="127.0.0.1")
    port: int=field(default=31775)
    def astuple(self) -> tuple:
        return astuple(self)

class Network:

    @staticmethod
    def msgsend(socket: sockets.socket, data: dict):
        "serialises and sends <data> over <socket> using msgpack"
        serialised = msgpack.dumps(data)
        packet = struct.pack(BYTE_COUNT_ENCODING, len(serialised)) + serialised
        socket.send(packet)

    @staticmethod
    def msgrecv(socket: sockets.socket, timeout: float = 10.) -> dict:
        "recieves packed packet from <socket> and returns it in the form of a dictionary"
        socket.setblocking(0)
        ready = select.select([socket], [], [], timeout)
        if ready[0]:
            lengthRaw = socket.recv(INFO_BYTES)
        else:
            return None
        try:
            length = struct.unpack(BYTE_COUNT_ENCODING, lengthRaw)[0]
        except struct.error:
            return None
        ready = select.select([socket], [], [], timeout)
        if ready[0]:
            raw = socket.recv(length)
        else:
            return None
        data = msgpack.loads(raw)
        return data

    @staticmethod
    def jsonsend(socket: sockets.socket, data: dict):
        "send a json packet over the given socket"
        serialised = json.dumps(data)
        msg = bytes(str(len(serialised)).rjust(DENARY_MAX_LENGTH_DIGITS, ZERO_STRING), ENCODING)
        socket.send(msg)
        socket.sendall(bytes(serialised, encoding=ENCODING))

    @staticmethod    
    def jsonrecv(socket: sockets.socket) -> dict:
        "recieve one json packet over the given socket"
        # read and interpret the length of the jsonsend packet
        length = str(socket.recv(DENARY_MAX_LENGTH_DIGITS), ENCODING)
        if length == "":
            return None
        length = int(length)
        # now get and deserialise the actual json packet
        view = memoryview(bytearray(length))
        offset = 0
        while length - offset > 0:
            recvSize = socket.recv_into(view[offset::], length - offset)
            offset += recvSize
        return json.loads(view.tobytes())

class Queue:
    "thread safe queue"
    def __init__(self):
        self.list = []
        self.lock = Lock()
        self.i = 0

    def __repr__(self) -> str:
        return "Q{}:{}".format(self.i, self.list)

    def __len__(self) -> int:
        return len(self.list) - self.i

    def dequeue(self) -> dict:
        with self.lock:
            if self.i >= len(self.list):
                return None
            element = self.list[self.i]
            self.i += 1
        return element

    def enqueue(self, element: dict):
        with self.lock:
            self.list.append(element)

class FixedQueue:
    "thread-safe fixed-length queue"
    def __init__(self, length=128):
        self.list = [None for x in range(length)]
        self.lock = Lock()
        self.read = 0
        self.write = 0
        self.length = length

    def __repr__(self) -> str:
        return f"FQ: size={self.length} read={self.read} write={self.write}"

    def enqueue(self, element: dict):
        with self.lock:
            self.list[self.write % self.length] = element
            self.write += 1
        if self.write > self.read + self.length:
            raise IndexError(f"read {self.read} equals write {self.write}! Queue wrote over self!")
    
    def dequeue(self):
        element = None
        with self.lock:
            if self.read >= self.write:
                return None
            element = self.list[self.read % self.length]
            self.read += 1
        return element






