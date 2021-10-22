

from __future__ import annotations

from pong import *

client = PongClient(Address())

client._start()

stime = time.time()

i = 0
while True:
    i += 1
    dt = time.time() - stime
    stime = time.time()
    client.ponger.tick(dt)
    if i % 5 == 0:
        client.ponger.display(V(100, 30))
    elif i % 10 == 0:
        client.update()


