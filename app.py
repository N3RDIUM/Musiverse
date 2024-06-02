from screen import Screen
from curses import window

class App:
    def __init__(self):
        self.current = None
        self.screens = {}
        self.props   = {
            'keybinds': '[K]eybinds [H]ome [Q]uit'
        }

    def add_screen(self, name: str, screen: Screen):
        self.screens[name] = screen
        if not self.current:
            self.current = name

    def navigate(self, name: str):
        self.props['last_screen'] = self.current
        self.current = name

    def render(self, stdscr: window, frame: int, frame_rate: float):
        try:
            return self.screens[self.current]._render(stdscr, frame, frame_rate)
        except KeyError:
            raise KeyError(f'Unknown screen: {self.current}')
