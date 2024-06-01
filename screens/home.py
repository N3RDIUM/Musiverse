from screen import Screen
from curses import window

class Home(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int):
        h, w = stdscr.getmaxyx()
        for i in range(h):
            for j in range(w - 1):
                stdscr.addstr(i, j, 'a')