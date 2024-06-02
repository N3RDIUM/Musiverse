from app import App
from theme import DEFAULT
from curses import window, color_pair

FILLED = '━'
EMPTY  = ' '

class StatusBar:
    def __init__(self, app: App):
        self.app = app
        self.height = 4
        app.props['statusbar'] = self
        
    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        
        # Render progressbar
        stdscr.addstr(h - 4, 0, f'﹝{FILLED * int(frame % (w - 4))}{EMPTY * ((w - 4) - int(frame % (w - 4)))}﹞', color_pair(DEFAULT))
        
        # TODO: Render player status when you actually make a player
        frm = f'Frame: {frame} ({frame_rate:.2f} fps)'
        stdscr.addstr(h - 3, 0, frm + ' ' * (w - len(frm)), color_pair(DEFAULT))
        
        # Empty row
        stdscr.addstr(h - 2, 0, ' ' * w, color_pair(DEFAULT))
        
        # Render active keybinds
        kb = self.app.props['keybinds']
        stdscr.addstr(h - 1, 0, ' ' * (w - len(kb)) + kb, color_pair(DEFAULT))
