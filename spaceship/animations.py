import curses
import asyncio
import os
from curses import initscr
from random import choice, randint
from typing import Coroutine
from itertools import cycle

from spaceship.curses_tools import draw_frame, read_controls
from spaceship.constants import SPACESHIP_HEIGHT, SPACESHIP_WIDTH, WINDOW_BORDER, FRAMES_PATH, STARS
from spaceship.utils import boost_spaceship_speed, choice_height, choice_width, sleep

canvas = initscr()
canvas.keypad(1)
rocket_frames = []
trash_frames = []

for frame_name in os.listdir(FRAMES_PATH):
    frame_name_head = frame_name.split("_")[0]
    match frame_name_head:
        case "rocket":
            with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
                rocket_frames.append(f.read())
        case "trash":
            with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
                trash_frames.append(f.read())


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


async def fly_garbage(canvas, column, garbage_frame, speed=0.4):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas, frames):
    _, columns_number = canvas.getmaxyx()
    while True:
        global coroutines
        coroutines.append(fly_garbage(
            canvas, randint(1, columns_number), choice(frames)))
        await sleep(18)


async def blink(canvas, row: int, column: int, offset_tics: int, symbol='*') -> Coroutine:
    """
    Анимация звезды
    """
    await sleep(offset_tics)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


async def animate_spaceship(canvas, initial_row: int, initial_column: int, frames: list[str]):
    """
    Анимация корабля
    """

    window_height, window_width = curses.window.getmaxyx(canvas)
    frames: cycle[str] = cycle(frames)  # type:ignore
    for frame in frames:
        for _ in range(2):
            user_row, user_column, _ = read_controls(canvas)

            boosted_row = boost_spaceship_speed(user_row)
            boosted_column = boost_spaceship_speed(user_column)

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
            await asyncio.sleep(0)
            draw_frame(canvas, initial_row, initial_column,
                       frame, negative=True)


coroutines: list[Coroutine] = [
    fire(canvas, 10, 30),
    animate_spaceship(canvas, 10, 30, rocket_frames),
    fill_orbit_with_garbage(canvas, trash_frames)
]
coroutines.extend(
    [blink(canvas,
           choice_height(canvas),
           choice_width(canvas),
           randint(1, 15),
           choice(STARS)
           )
     for _ in range(40)
     ]
)
