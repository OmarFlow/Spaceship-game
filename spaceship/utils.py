import random
import curses


def choice_height(c) -> int:
    return random.randint(1, curses.window.getmaxyx(c)[0] - 1)


def choice_width(c) -> int:
    return random.randint(1, curses.window.getmaxyx(c)[1] - 1)
