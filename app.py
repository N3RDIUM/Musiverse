from screen import Screen
from curses import window
from storage import Storage

class App:
    def __init__(self):
        self.current = None
        self.screens = {}
        self.props   = {
            'keybinds': '[Q]uit',
            'keylock': False,
            'status_text': '',
            'queue': [],
        }
        self.storage = Storage(self)

    def add_screen(self, name: str, screen: Screen):
        self.screens[name] = screen
        if not self.current:
            self.current = name

    def navigate(self, name: str):
        self.props['last_screen'] = self.current
        self.current = name
        try: self.screens[self.current].on_navigate()
        except AttributeError: pass

    def render(self, stdscr: window, frame: int, frame_rate: float):
        try:
            return self.screens[self.current]._render(stdscr, frame, frame_rate)
        except KeyError:
            raise KeyError(f'Unknown screen: {self.current}')
        
    def on_kill(self):
        try: self.screens[self.current].on_kill()
        except AttributeError: pass
        self.storage.kill()
