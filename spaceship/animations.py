import curses
import asyncio
from typing import Coroutine
from itertools import cycle

from spaceship.curses_tools import draw_frame, read_controls
from spaceship.constants import SPACESHIP_HEIGHT, SPACESHIP_WIDTH, WINDOW_BORDER
from spaceship.utils import boost_spaceship_speed


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


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
    window_height, window_width = curses.window.getmaxyx(canvas)
    frames: cycle[str] = cycle(frames)  # type:ignore
    for frame in frames:
        user_row, user_colum, _ = read_controls(canvas)

        boosted_row = boost_spaceship_speed(user_row)
        boosted_column = boost_spaceship_speed(user_colum)

        initial_row += boosted_row
        initial_column += boosted_column

        if initial_row < WINDOW_BORDER:
            initial_row = WINDOW_BORDER
        elif initial_row > window_height - SPACESHIP_HEIGHT:
            initial_row = window_height - SPACESHIP_HEIGHT

        if initial_column < WINDOW_BORDER:
            initial_column = WINDOW_BORDER
        elif initial_column > window_width - SPACESHIP_WIDTH:
            initial_column = window_width - SPACESHIP_WIDTH

        draw_frame(canvas, initial_row, initial_column, frame)
        draw_frame(canvas, initial_row, initial_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, initial_row, initial_column,
                   frame, negative=True)

