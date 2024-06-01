from app import App
from curses import window

FILLED = '━'
EMPTY  = ' '

class StatusBar:
    def __init__(self, app: App):
        self.app = app
        self.height = 3
        app.props['statusbar'] = self
        
    def render(self, stdscr: window, frame: int):
        h, w = stdscr.getmaxyx()
        
        # Render progressbar
        stdscr.addstr(h - 3, 0, f'﹝{FILLED * int(frame % (w - 4))}{EMPTY * ((w - 4) - int(frame % (w - 4)))}﹞')
        
        # TODO: Render player status
        stdscr.addstr(h - 2, 0, f'Frame: {frame}')
        
        # Render active keybinds
        stdscr.addstr(h - 1, 0, self.app.props['keybinds'])
