import time
from typing import List, Coroutine, Tuple
from itertools import cycle

from spaceship.help_code import *
from spaceship.utils import *
from spaceship.constants import TIC_TIMEOUT


async def blink(canvas, row: int, column: int, symbol='*') -> Coroutine:
    """
    Анимация звезды
    """
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(1, 10)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(1, 10)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(random.randint(1, 10)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(1, 10)):
            await asyncio.sleep(0)


async def animate_spaceship(canvas, sr: int, sc: int, text: Tuple[str, str]):
    """
    Анимация корабля
    """
    canvas.nodelay(True)
    max_row: int = curses.window.getmaxyx(canvas)[0]
    max_column: int = curses.window.getmaxyx(canvas)[1]
    while True:
        for frame in cycle(text):
            draw_frame(canvas, sr, sc, frame)

            r = sr
            c = sc

            row, col, _ = read_controls(canvas)
            sr += row
            sc += col

            if sr < 1 or sr > max_row - 10:
                sr = r
            if sc < 1 or sc > max_column - 6:
                sc = c

            draw_frame(canvas, r, c, frame, negative=True)
            draw_frame(canvas, sr, sc, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, sr, sc, frame, negative=True)


def draw(canvas) -> None:
    """
    Основной метод отрисовки
    """
    canvas.border()

    with open("../frames/rocket_frame_1.txt", "r") as f:
        frame1 = f.read()

    with open("../frames/rocket_frame_2.txt", "r") as f:
        frame2 = f.read()

    coroutines: List[Coroutine] = [
        animate_spaceship(canvas, 10, 30, (frame1, frame2))]
    coroutines.extend([blink(canvas, choice_height(canvas), choice_width(
        canvas), choice_star()) for _ in range(30)])

    while True:
        canvas.refresh()
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
