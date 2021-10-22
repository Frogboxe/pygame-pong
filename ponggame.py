
from __future__ import annotations

import time
from random import randint

from element import Element
from pong import Pong
from pyg import Screen, load_and_scale, load_texture, TEXTURE_ROUTES, LOG_ROUTES
from pygcontext import PygContext
from pygtext import Text
from unsafe_vector import V, Vector

class Display(Screen):
    _size = Pong.pageSize

INPUT_SMOOTHING = 4

class Pogn(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_texture("pogchamp.png")

class Ball(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale(f"{str(randint(0, 5))}.png", Pong.ballSize)

class Paddle(Element):
    def __init__(self, screen, pos: Vector):
        super().__init__(screen, pos)
        self.texture = load_and_scale("4.png", Pong.paddleSize)

class BlackBackground(Element):
    def __init__(self, screen):
        super().__init__(screen, V(0, 0))
        self.texture = load_and_scale("background.png", Pong.pageSize)

class Scoreboard(Text):
    fontSize = 32


class PongGameContext(PygContext):

    BallType: type = Ball
    last: float
    ballCount: int = 800
    
    ponger: Pong = Pong()
    background: BlackBackground
    balls: list[Ball]
    paddles: list[Paddle]
    score: Vector
    scoreboard: Scoreboard
    dt: float = 0

    def start(self):
        super().start()
        self.exitCode = 0
        self.last = time.time()
        self.ponger.create_game_balls(self.ballCount)
        self.background = BlackBackground(self.screen)
        self.balls = [self.BallType(self.screen, pos) for pos in self.ponger.balls]
        self.paddles = [Paddle(self.screen, self.ponger.paddles[i]) for i in range(2)]
        self.score = V(0, 0)
        self.scoreboard = Scoreboard(self.screen, self.ponger.pageSize.vx / 2 + self.ponger.pageSize.vy / 8)
        self.scoreboard.text = f"  {0}  :  {0}  "
        self.scoreboard.pos = self.scoreboard.pos - (self.scoreboard.size.vx / 2)
        self.frames = 0
        self.startTime = time.time()

    def game_pogn(self):
        self.ponger.ballSize = V(64, 64)
        self.screen.caption = "Pogn"
        self.BallType = Pogn

    def game_pong(self):
        self.ponger.ballSize = V(6, 6)
        self.screen.caption = "Pong"
        self.BallType = Ball

    def tend_paddle(self, paddleID: int, target: Vector, dt: float):
        self.ponger.paddleInput[paddleID] = self.ponger.paddleInput[paddleID].approach(target, factor=INPUT_SMOOTHING * dt)

    def handle_input(self, dt: float):
        keys = self.screen.keys
        if all((i not in keys) for i in (119, 115, 97, 100)):
            self.tend_paddle(0, V(0, 0), dt)
        else:
            if 119 in keys: # w
                self.tend_paddle(0, V(0, -1), dt)
            if 115 in keys: # s
                self.tend_paddle(0, V(0, 1), dt)
            if 97 in keys:
                self.tend_paddle(0, V(-1, 0), dt)
            if 100 in keys:
                self.tend_paddle(0, V(1, 0), dt)
        if all(i not in keys for i in (1073741906, 1073741905, 1073741904, 1073741903)):
            self.tend_paddle(1, V(0, 0), dt)
        else:
            if 1073741906 in keys: # up arrow
                self.tend_paddle(1, V(0, -1), dt)
            if 1073741905 in keys: # down arrow
                self.tend_paddle(1, V(0, 1), dt)
            if 1073741904 in keys: # left arrow
                self.tend_paddle(1, V(-1, 0), dt)
            if 1073741903 in keys: # right arrow
                self.tend_paddle(1, V(1, 0), dt)

    def key_down(self, k: int):
        if 32 in self.screen.keys:
            self.screen.done = True
            self.exitCode = 1

    def handle_scoreboard(self):
        if self.score != self.ponger.score:
            s1, s2 = str(self.ponger.score.y), str(self.ponger.score.x)
            s1, s2 = s1.rjust(4, " "), s2.ljust(4, " ")
            self.scoreboard.text = f"  {s1}  :  {s2}  "
            self.scoreboard.pos = (self.ponger.pageSize.vx / 2 + self.ponger.pageSize.vy / 8) - (self.scoreboard.size.vx / 2)
            self.score = self.ponger.score

    def handle_tick(self) -> float:
        ctime = time.time()
        dt = ctime - self.last
        self.last = ctime
        self.ponger.tick(dt)
        return dt

    def handle_elements(self):
        for i, ball in enumerate(self.ponger.balls):
            self.balls[i].pos = ball
        for i, paddle in enumerate(self.ponger.paddles):
            self.paddles[i].pos = paddle
        self.screen.changed = True

    def update(self):
        self.handle_input(self.dt)
        self.handle_scoreboard()
        self.dt = self.handle_tick()
        self.handle_elements()

def main(d: bool = True):
    if d:
        TEXTURE_ROUTES, LOG_ROUTES = "\\assets", "\\logs"
    screen = Display()
    while True:
        ta = PongGameContext(screen)
        ta.ponger = Pong()
        ta.game_pong()
        with ta:
            screen.run(2000, 2000)
        if ta.exitCode == 0:
            break
        tb = PongGameContext(screen)
        tb.ponger = Pong()
        tb.game_pogn()
        with tb:
            screen.run(2000, 2000)
        if tb.exitCode == 0:
            break

if __name__ == "__main__":
    main(False)


