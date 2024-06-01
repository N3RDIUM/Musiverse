from screen import Screen
from curses import window

class App:
    def __init__(self):
        self.current = None
        self.screens = {}
        self.props   = {}

    def add_screen(self, name: str, screen: Screen):
        self.screens[name] = screen
        if not self.current:
            self.current = name

    def navigate(self, name: str):
        self.current = name

    def render(self, stdscr: window, frame: int):
        try:
            return self.screens[self.current].render(stdscr, frame)
        except KeyError:
            raise KeyError(f'Unknown screen: {self.current}')