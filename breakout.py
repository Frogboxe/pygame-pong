
from __future__ import annotations

import os
import sys
from contextlib import suppress
from functools import cached_property
from math import atan, pi

from pyserve import create_log_target, initialise_log_manager
from vector import V, Vector, A, Angle

# work out where the program is running to find texture files.
ROUTE = "\\".join(sys.argv[0].split("\\")[:-1:]) + "\\"
ROUTE_ALT = "/".join(sys.argv[0].split("/")[:-1:]) + "/"
# sometimes the route given by sys.argv[0] uses `/` as a split and sometimes `\`
# so this hack fixes that
if len(ROUTE) < len(ROUTE_ALT):
    ROUTE = ROUTE_ALT
LOG_ROUTES = ROUTE + "logs/"

# hacky assemble logs folder
with suppress(OSError):
    os.mkdir(LOG_ROUTES)

# logs setup
LM = initialise_log_manager()
breakout = create_log_target("breakout", f"{LOG_ROUTES}breakout.log")
LM.add_files([breakout])

log = LM.create_log({"breakout", "stdout"}, defaultKwargs={"flush": True})

class Breakout:

    pageSize: Vector = V(1500, 1000)

    score: int = 0

    paddles: list[Vector]
    balls: list[Vector]
    blocks: list[Vector]

    ballVelocities: list[Vector]

    paddleInput: list[Vector] = []

    paddleSize: Vector = V(140, 24)
    paddleOffset: Vector = V(0, 20)
    paddleMaxSpeed: Vector = V(900, 600)
    paddleElasticity: Vector = V(1, 1)
    paddlePlayableSize: Vector = (pageSize.vy / 2)

    ballSize: Vector = V(6, 6)
    ballSpeedLow: Vector = V(1, 1)
    ballSpeedHigh: Vector = V(2, 2)
    ballSpeedRNGScale: float = 0.5
    ballIdealSpeed: Vector = V(100, 200)
    ballReturnToIdealFactor: float = 0.001
    ballStartSpeed: Vector = V(0, 100)
    ballStartLocation: Vector = (pageSize.vy / 4) + (pageSize.vx / 2)
    ballBaseSpeed: Vector = V(100, 100)
    ballBumpMultiplier: Vector = V(1, 1)

    blockSize: Vector = V(42, 32)

    def create_game_normal(self):
        self.balls = [self.ballStartLocation for _ in range(1)]
        self.ballVelocities = [self.ballStartSpeed * Vector.from_random_sign() * Vector.from_random_square(self.ballSpeedLow, self.ballSpeedHigh) * self.ballSpeedRNGScale for _ in range(1)]
        self.paddles = [(self.pageSize.vy - self.paddleSize.vy - self.paddleOffset.vy) 
        + ((self.pageSize.vx) / 2 - (self.paddleSize.vx))]
        self.paddleInput = [V(0, 0)]
        xdc = (self.pageSize.x // (self.blockSize.x)) - 1
        self.blocks = []
        for j in range(4):
            self.blocks.extend([V(self.blockSize.x * i + ((j % 2) * (self.blockSize.x / 2)), self.blockSize.y * j) for i in range(xdc)])

    def move_paddles(self, dt: float):
        for i, paddle in enumerate(self.paddles):
            paddleInput = self.paddleInput[i].bind(V(-1, -1), V(1, 1))
            self.paddles[i] = (paddle + (self.paddleMaxSpeed * paddleInput * dt)).bind(self.pageSize.vy - self.paddlePlayableSize, 
            self.pageSize - self.paddleOffset - self.paddleSize)

    def passive_speed_modification(self):
        for i, currentVelocity in enumerate(self.ballVelocities):
            signs = currentVelocity.signs()
            self.ballVelocities[i] = signs * abs(currentVelocity).approach(self.ballIdealSpeed, self.ballReturnToIdealFactor)

    def block_collision(self, candidate: Vector, i: int, j: int, block: Vector):
        blockCentre = block + (self.blockSize / 2)
        candidateCentre = candidate + (self.ballSize / 2)
        velocity = (self.ballVelocities[i] * self.ballBumpMultiplier)
        angle = A(vector=(blockCentre - candidateCentre)).radians
        full = A(degrees=360).radians
        half = A(degrees=180).radians
        theta = self.theta.radians
        if angle <= theta and angle >= (full - theta):
            # top of paddle
            self.ballVelocities[i] = velocity.vx + -abs(velocity.vy)
        elif angle >= theta and angle <= (half - theta):
            # left side
            self.ballVelocities[i] = -abs(velocity.vx) + velocity.vy
        elif angle >= (half - theta) and angle <= (half + theta):
            # bottom
            self.ballVelocities[i] = velocity.vx + abs(velocity.vy)
        else:
            # right side
            self.ballVelocities[i] = abs(velocity.vx) + velocity.vy

    def paddle_collision(self, candidate: Vector, i: int, j: int, paddle: Vector):
        paddleCentre = paddle + (self.paddleSize / 2)
        candidateCentre = candidate + (self.ballSize / 2)
        angle = A(vector=(paddleCentre - candidateCentre)).radians
        full = A(degrees=360).radians
        half = A(degrees=180).radians
        theta = self.theta.radians
        #              <initial velocity>                            <paddle velocity>                              <scale up from collision>
        velocity = ((self.ballVelocities[i] + (self.paddleInput[j] * self.paddleMaxSpeed * self.paddleElasticity)) * self.ballBumpMultiplier)
        if angle <= theta and angle >= (full - theta):
            # top of paddle
            self.ballVelocities[i] = velocity.vx + -abs(velocity.vy)
        elif angle >= theta and angle <= (half - theta):
            # left side
            self.ballVelocities[i] = -abs(velocity.vx) + velocity.vy
        elif angle >= (half - theta) and angle <= (half + theta):
            # bottom
            self.ballVelocities[i] = velocity.vx + abs(velocity.vy)
        else:
            # right side
            self.ballVelocities[i] = abs(velocity.vx) + velocity.vy

    def wall_collision(self, i: int, candidate: Vector):
        velocity = self.ballVelocities[i]
        # top collision
        if candidate.y < 0:
            self.ballVelocities[i] = velocity.vx + abs(velocity.vy)
        elif candidate.y > (self.pageSize.y - self.ballSize.y):
            self.ballVelocities[i] = velocity.vx + -abs(velocity.vy)
        # side collision
        if candidate.x < 0:
            self.ballVelocities[i] = abs(velocity.vx) + velocity.vy
        elif candidate.x > (self.pageSize.x - self.ballSize.x):
            self.ballVelocities[i] = -abs(velocity.vx) + velocity.vy

    def tick(self, dt: float):
        self.move_paddles(dt)
        self.passive_speed_modification()
        # ball behaviour
        for i, ball in enumerate(self.balls):
            # destroy balls at bottom
            if self.balls[i] is None or self.balls[i].y > self.pageSize.y - self.paddleOffset.y:
                self.balls[i] = None
                continue
            # ball movement
            candidate: Vector = ball + self.ballVelocities[i] * dt
            for j, paddle in enumerate(self.paddles):
                if any((
                    candidate.inside(paddle, paddle + self.paddleSize),
                    (candidate + self.ballSize.vx).inside(paddle, paddle + self.paddleSize),
                    (candidate + self.ballSize.vy).inside(paddle, paddle + self.paddleSize),
                    (candidate + self.ballSize).inside(paddle, paddle + self.paddleSize)
                )):
                    self.paddle_collision(candidate, i, j, paddle)
            for j, block in enumerate(self.blocks):
                if block is None:
                    continue
                if any((
                    candidate.inside(block, block + self.blockSize),
                    (candidate + self.ballSize.vx).inside(block, block + self.blockSize),
                    (candidate + self.ballSize.vy).inside(block, block + self.blockSize),
                    (candidate + self.ballSize).inside(block, block + self.blockSize)
                )):
                    self.block_collision(candidate, i, j, block)
                    self.blocks[j] = None
            self.wall_collision(i, candidate)
            self.balls[i] = candidate

    @cached_property
    def theta(self) -> float:
        # for a rectangle where the top two points are p1, p2 and the origin is o
        # theta is precisely half the angle described p1 <- o -> p2 (p1 o p2) 
        # this is used to distinguish between which side of the paddle was hit
        # by a ball
        #return (360 * (atan(self.paddleSize.x / self.paddleSize.y) / (2 * pi)))
        return A(radians=(atan(self.paddleSize.x / self.paddleSize.y)))

    @cached_property
    def block_theta(self) -> float:
        # theta but for blocks instead of paddles
        #return (360 * (atan(self.blockSize.x / self.blockSize.y) / (2 * pi)))
        return A(radians=(atan(self.blockSize.x / self.blockSize.y)))



