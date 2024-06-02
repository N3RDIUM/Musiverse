from app import App
from theme import STATUSBAR
from curses import window, color_pair

FILLED = '━'
EMPTY  = ' '
DELIM  = '﹝﹞'

class StatusBar:
    def __init__(self, app: App):
        self.app = app
        self.height = 4
        app.props['statusbar'] = self
        
    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        
        # ROW 1: Progress bar
        # ROW 2: timestamps and media ctrl status and media info (scrolling song name)
        # ROW 3: empty
        # ROW 4: keybinds and status text
        
        # Render progressbar
        stdscr.addstr(h - 4, 0, f'{DELIM[0]}{FILLED * int(frame % (w - 4))}{EMPTY * ((w - 4) - int(frame % (w - 4)))}{DELIM[1]}', color_pair(STATUSBAR))
        
        # TODO: Render player status when you actually make a player
        frm = f'Frame: {frame} ({frame_rate:.2f} fps)  /        '
        stdscr.addstr(h - 3, 0, frm + ' ' * (w - len(frm)), color_pair(STATUSBAR))
        
        # Empty rows
        stdscr.addstr(h - 2, 0, ' ' * w, color_pair(STATUSBAR))
        
        # Render active keybinds
        kb = self.app.props['keybinds']
        lt = 'asdf' * 10 # app.props['status_text']
        if len(lt) > w - len(kb) - 4:
            lt = lt[0 : w - len(kb) - 4] + '...'
        stdscr.addstr(h - 1, 0, lt + ' ' * (w - len(kb) - len(lt)) + kb, color_pair(STATUSBAR))
