import random
import curses

from spaceship.constants import STARS


def choice_height(c) -> int:
    return random.randint(1, curses.window.getmaxyx(c)[0] - 1)


def choice_width(c) -> int:
    return random.randint(1, curses.window.getmaxyx(c)[1] - 1)


def choice_star() -> str:
    return random.choice(STARS)
