import random
import curses
from typing import Coroutine

from spaceship.constants import BOOST


def choice_height(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[0] - 1)


def choice_width(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[1] - 1)


def boost_spaceship_speed(row: int, rate: float) -> int:
    if row > 0:
        return row + (BOOST * rate)
    elif row < 0:
        return row - (BOOST * rate)
    return row


class Sleep:
    def __init__(self, tics: int):
        self.tics = tics

    def __await__(self):
        while self.tics >= 0:
            yield 1
            self.tics -= 1


async def sleep(tics=1) -> Coroutine:
    await Sleep(tics)
