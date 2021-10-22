
from __future__ import annotations

from numba import njit, prange
import numpy as np

class FakeBall: x: float; y: float; dx: float; dy: float
class FakePaddle: x: float; y: float

BALL = np.dtype([('x', np.float64),
                 ('y', np.float64),
                 ('dx', np.float64),
                 ('dy', np.float64)])

PADDLE = np.dtype([('x', np.float64), ('y', np.float64)])

BALLX = 6
BALLY = 6
PADDLEX = 40
PADDLEY = 100

PAGEX = 1500
PAGEY = 1000

ballCount, paddleCount = 1_000_000, 2

@njit(parallel=True)
def tick(balls: list[FakeBall], paddles: list[FakePaddle], dt: np.float64):
    # all ball -> paddle / wall collision
    for i in prange(ballCount):
        # setup
        record = balls[i]
        x, y, dx, dy = record.x, record.y, record.dx, record.dy
        # paddle collision
        for j in prange(paddleCount):
            precord = paddles[j]
            px, py = precord.x, precord.y
            wx, wy = px + PADDLEX, py + PADDLEY
            
        # wall collision

    return balls

ballBuffer = np.zeros(ballCount * len(BALL)).reshape((ballCount, len(BALL))).astype(np.float64)
balls = np.recarray(ballCount, dtype=BALL, buf=ballBuffer)

paddleBuffer = np.zeros(paddleCount * len(PADDLE)).reshape((paddleCount, len(PADDLE))).astype(np.float64)
paddles = np.recarray(paddleCount, dtype=PADDLE, buf=paddleBuffer)

for i in range(1_000):
    tick(balls, paddles, 0.1)

print(balls[4].x)