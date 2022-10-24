import random
import curses

from spaceship.constants import BOOST


def choice_height(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[0] - 1)


def choice_width(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[1] - 1)


def boost_spaceship_speed(row: int) -> int:
    if row > 0:
        return row + BOOST
    elif row < 0:
        return row - BOOST
    return row
