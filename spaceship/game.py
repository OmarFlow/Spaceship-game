import time
import curses

from spaceship.constants import TIC_TIMEOUT
from spaceship.animations import coroutines, canvas  # noqa


def draw(canvas) -> None:
    """
    Основной метод отрисовки
    """
    canvas.nodelay(True)

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
    curses.curs_set(False)
    draw(canvas)
