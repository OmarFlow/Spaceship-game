import time
import curses
from typing import Coroutine
import os
from random import choice, randint

from spaceship.utils import choice_height, choice_width
from spaceship.constants import TIC_TIMEOUT, FRAMES_PATH, STARS
from spaceship.animations import fire, animate_spaceship, blink


def draw(canvas) -> None:
    """
    Основной метод отрисовки
    """
    canvas.border()
    canvas.nodelay(True)

    frames = []

    for frame_name in os.listdir(FRAMES_PATH):
        with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
            frames.append(f.read())

    coroutines: list[Coroutine] = [
        fire(canvas, 10, 30),
        animate_spaceship(canvas, 10, 30, frames)
    ]
    coroutines.extend(
        [blink(canvas,
               choice_height(canvas),
               choice_width(canvas),
               randint(1, 15),
               choice(STARS)
               )
         for _ in range(30)
         ]
    )

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
