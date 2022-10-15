import time
import curses
from typing import Coroutine
import os
from itertools import cycle
from random import choice, randint
import asyncio

from spaceship.devman_help import draw_frame, read_controls
from spaceship.utils import choice_height, choice_width
from spaceship.constants import TIC_TIMEOUT, SPACESHIP_HEIGHT, SPACESHIP_WIDTH, FRAMES_PATH, STARS


async def blink(canvas, row: int, column: int, offset_tics: int, symbol='*') -> Coroutine:
    """
    Анимация звезды
    """

    for _ in range(offset_tics):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def animate_spaceship(canvas, initial_row: int, initial_column: int, frames: list[str]):
    """
    Анимация корабля
    """
    max_window_height, max_window_width = curses.window.getmaxyx(canvas)
    frames: cycle[str] = cycle(frames)  # type:ignore
    while True:
        for frame in frames:
            user_row, user_colum, _ = read_controls(canvas)
            initial_row += user_row
            initial_column += user_colum

            if initial_row < 1 or initial_row > max_window_height - SPACESHIP_HEIGHT:
                initial_row -= user_row
            if initial_column < 1 or initial_column > max_window_width - SPACESHIP_WIDTH:
                initial_column -= user_colum

            draw_frame(canvas, initial_row, initial_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, initial_row, initial_column,
                       frame, negative=True)


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
