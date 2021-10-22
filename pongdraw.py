
from __future__ import annotations

import time

from element import Element
from pong import INPUT, PADDLE_ID, Pong, PongClient
from pyg import Screen, load_and_scale
from pygcontext import PygContext
from pyserve import Address
from vector import V, Vector


class Display(Screen):
    _size = Pong.pageSize

class Context(PygContext):
    def start(self):
        super().start()
        self.last = time.time()
        self.background = BlackBackground(self.screen)
        self.ball = Ball(self.screen, self.client.ponger.balls[0])
        self.paddles = [Paddle(self.screen, self.client.ponger.paddles[i]) for i in range(2)]
        self.i = 0

    def update(self):
        keys = self.screen.keys
        if 119 in keys:
            self.client.message[INPUT] = -1
            self.client.ponger.paddleInput[0] = V(0, -1)
        elif 115 in keys:
            self.client.message[INPUT] = 1
            self.client.ponger.paddleInput[0] = V(0, 1)
        else:
            self.client.message[INPUT] = 0
            self.client.ponger.paddleInput[0] = V(0, 0)
        if 1073741906 in keys:
            print("^")
        if 1073741905 in keys:
            print("v")
        if self.i % 2 == 0:
            ctime = time.time()
            utime = self.client.updatetime
            rdt = ctime - (self.last * (self.last > utime) + utime * (self.last <= utime))
            self.last = ctime
            self.client.ponger.tick(rdt, self.i % 2 == 0)
            self.ball.pos = self.client.ponger.balls[0]
            for i, paddle in enumerate(self.client.ponger.paddles):
                self.paddles[i].pos = paddle
        self.i += 1
        self.screen.changed = True

class Ball(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale("ball.png", Pong.ballSize)

class Paddle(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale("ball.png", Pong.paddleSize)

class BlackBackground(Element):
    def __init__(self, screen):
        super().__init__(screen, V(0, 0))
        self.texture = load_and_scale("background.png", Pong.pageSize)

screen = Display()
client = PongClient(Address())
client._start()
with client.update():
    context = Context(screen)
    context.client = client
    with context:
        screen.run(144, 144)


