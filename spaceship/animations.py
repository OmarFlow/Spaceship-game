import curses
import asyncio
import os
from curses import initscr
from random import choice, randint
from typing import Coroutine
from itertools import cycle

from spaceship.curses_tools import draw_frame, read_controls, Obstacle, get_frame_size, get_garbage_delay_tics
from spaceship.constants import (SPACESHIP_HEIGHT, SPACESHIP_WIDTH, WINDOW_BORDER, FRAMES_PATH, STARS,
                                 BOOST, BOOST_RATE, EXPLOSION_FRAMES, PHRASES, START_YEAR, SHOW_GAMEOVER_DURATION,
                                 UNLOCK_GUN_YEAR)
from spaceship.utils import boost_spaceship_speed, choice_height, choice_width, sleep

canvas = initscr()
canvas.keypad(1)
rocket_frames = []
trash_frames = []
gameover_frames = []
obstacles = dict()
to_explode = dict()
year = START_YEAR

for frame_name in os.listdir(FRAMES_PATH):
    frame_name_head = frame_name.split("_")[0]
    match frame_name_head:
        case "rocket":
            with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
                rocket_frames.append(f.read())
        case "trash":
            with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
                trash_frames.append(f.read())
        case "game":
            with open(os.path.join(FRAMES_PATH, frame_name), 'r') as f:
                gameover_frames.append(f.read())


async def explode(canvas, center_row: int, center_column: int) -> None:
    rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in EXPLOSION_FRAMES:

        draw_frame(canvas, corner_row, corner_column, frame)

        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)


async def blink(canvas, row: int, column: int, offset_tics: int, symbol='*') -> None:
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


async def show_gameover(canvas, row: int, column: int, frame) -> None:
    draw_frame(canvas, row, column, frame)
    await sleep(SHOW_GAMEOVER_DURATION)
    draw_frame(canvas, row, column,
               frame, negative=True)


async def increase_year() -> None:
    global year
    while True:
        await sleep(15)
        year += 1


async def show_years(canvas) -> None:
    y, x = canvas.getmaxyx()
    subwin = canvas.derwin(2, x, y - 2, 0)
    while True:
        subwin.addstr(0, 1,  f'{year}')
        if phrase := PHRASES.get(year):
            subwin.addstr(1, 1, phrase)
        subwin.refresh()
        subwin.clear()
        await sleep(0)


async def fire(canvas, start_row: int, start_column: int, rows_speed=-0.3, columns_speed=0) -> None:
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
        for obstacle in obstacles.values():
            if obstacle.has_collision(row, column):
                to_explode[id(obstacle)] = True
                return

        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def burst_fire(canvas, row: int, column: int) -> None:
    for _ in range(3):
        coroutines.append(fire(canvas, row, column)),
        await sleep(1)


async def animate_spaceship(canvas, initial_row: int, initial_column: int, frames: list[str]) -> None:
    """
    Анимация корабля
    """

    window_height, window_width = curses.window.getmaxyx(canvas)
    frames: cycle[str] = cycle(frames)  # type:ignore
    boost_row_rate = BOOST_RATE
    boost_column_rate = BOOST_RATE
    for frame in frames:
        print(window_height)
        for _ in range(2):
            user_row, user_column, is_fire = read_controls(canvas)

            for obstacle in obstacles.values():
                if obstacle.has_collision(initial_row, initial_column):
                    coroutines.append(show_gameover(canvas, initial_row, initial_column, choice(gameover_frames)))
                    return
            boosted_row = boost_spaceship_speed(user_row, boost_row_rate)
            boosted_column = boost_spaceship_speed(user_column, boost_column_rate)

            if not user_row:
                boost_row_rate = BOOST_RATE
                boost_column_rate = BOOST_RATE
            elif boost_row_rate < BOOST:
                boost_row_rate += BOOST_RATE
                boost_column_rate += BOOST_RATE

            initial_row += boosted_row
            initial_column += boosted_column
            initial_row = sorted([window_height - SPACESHIP_HEIGHT, WINDOW_BORDER, initial_row])[1]
            initial_column = sorted([window_width - SPACESHIP_WIDTH, WINDOW_BORDER, initial_column])[1]

            if is_fire and year > UNLOCK_GUN_YEAR:
                coroutines.append(burst_fire(canvas, initial_row, initial_column))

            draw_frame(canvas, initial_row, initial_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, initial_row, initial_column,
                       frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.4) -> None:
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    row_size, column_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows_size=row_size, columns_size=column_size)
    obstacles[id(obstacle)] = obstacle

    while row < rows_number:
        if to_explode.get(id(obstacle)):
            coroutines.append(explode(canvas, row, column))
            del to_explode[id(obstacle)]
            del obstacles[id(obstacle)]
            return

        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row = row
    del obstacles[id(obstacle)]


async def fill_orbit_with_garbage(canvas, frames) -> None:
    _, columns_number = canvas.getmaxyx()
    while True:
        if year < 1961:
            await sleep(0)
            continue
        coroutines.append(fly_garbage(
            canvas, randint(1, columns_number), choice(frames)))
        await sleep(get_garbage_delay_tics(year))


coroutines: list[Coroutine] = [
    fire(canvas, 10, 30),
    animate_spaceship(canvas, 10, 30, rocket_frames),
    fill_orbit_with_garbage(canvas, trash_frames),
    show_years(canvas),
    increase_year()
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
