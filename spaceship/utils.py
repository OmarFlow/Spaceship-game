import random
import curses


def choice_height(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[0] - 1)


def choice_width(canvas) -> int:
    return random.randint(1, curses.window.getmaxyx(canvas)[1] - 1)
