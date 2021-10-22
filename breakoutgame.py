
from __future__ import annotations

import time
from random import randint

from breakout import Breakout, log
from element import Element
from pyg import Screen, load_and_scale
from pygcontext import PygContext
from vector import V, Vector


class Display(Screen):
    _size = Breakout.pageSize
    caption = "Breakout"

class DontRenderWhenPosNoneElement(Element):
    @property
    def pos(self) -> Vector:
        return self._pos

    @pos.setter
    def pos(self, pos: Vector):
        self._pos = pos
        if pos is None:
            self.render = False

class Ball(DontRenderWhenPosNoneElement):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale(f"{str(randint(0, 5))}.png", Breakout.ballSize)

class Paddle(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale("4.png", Breakout.paddleSize)

class BlackBackground(Element):
    def __init__(self, screen):
        super().__init__(screen, V(0, 0))
        self.texture = load_and_scale("background.png", Breakout.pageSize)

class Block(DontRenderWhenPosNoneElement):
    def __init__(self, screen: Display, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale(f"{str(randint(0, 5))}.png", Breakout.blockSize)

INPUT_SMOOTHING = 8

class BreakoutGameContext(PygContext):

    breaker: Breakout = Breakout()
    background: BlackBackground
    balls: list[Ball]
    paddles: list[Paddle]
    blocks: list[Block]
    score: int
    dt: float = 0

    def start(self):
        super().start()
        self.exitCode = 0
        self.last = time.time()
        self.breaker.create_game_normal()
        self.background = BlackBackground(self.screen)
        self.balls = [Ball(self.screen, pos) for pos in self.breaker.balls]
        self.paddles = [Paddle(self.screen, self.breaker.paddles[i]) for i in range(1)]
        self.blocks = [Block(self.screen, pos) for pos in self.breaker.blocks]
        self.score = 0
    
    def tend_paddle(self, paddleID: int, target: Vector, dt: float):
        self.breaker.paddleInput[paddleID] = self.breaker.paddleInput[paddleID].approach(target, factor=INPUT_SMOOTHING * dt)

    def handle_input(self, dt: float):
        keys = self.screen.keys
        if all((i not in keys) for i in (119, 115, 97, 100)):
            self.tend_paddle(0, V(0, 0), dt)
        else:
            x, y = 0, 0
            x += 100 in keys
            x -= 97 in keys
            y += 115 in keys
            y -= 119 in keys
            self.tend_paddle(0, V(x, y), dt)

    def handle_tick(self) -> float:
        ctime = time.time()
        dt = ctime - self.last
        self.last = ctime
        self.breaker.tick(dt)
        return dt

    def handle_elements(self):
        for i, ball in enumerate(self.breaker.balls):
            self.balls[i].pos = ball
        for i, paddle in enumerate(self.breaker.paddles):
            self.paddles[i].pos = paddle
        for i, block in enumerate(self.breaker.blocks):
            self.blocks[i].pos = block
        self.screen.changed = True

    def update(self):
        self.handle_input(self.dt)
        self.dt = self.handle_tick()
        self.handle_elements()

    def key_down(self, k: int):
        if k == 32:
            self.screen.done = True
            self.exitCode = 1

screen = Display()
while True:
    game = BreakoutGameContext(screen)
    with game:
        screen.run(144, 144)
    if game.exitCode == 0:
        break



