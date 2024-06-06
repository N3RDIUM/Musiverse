from theme import DEFAULT, CURSOR
from screen import Screen
from curses import window, color_pair, KEY_BACKSPACE
from curses.ascii import ESC

_allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_ ."
ALLOWED = set([ord(i) for i in _allowed])

class Search(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = ""
        self.cursor_position = 0

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        h -= self.app.props['statusbar'].height
        render = [' ' * w for _ in range(h)]
        
        # Render the thing
        try:
            query = self.query
            cursor_position = self.cursor_position
            if(len(query) > w - 2):
                query = query[len(query) - (w - 2):]
                cursor_position = w - 3
            render[0] = "╭" + "─" * (w - 2) + "╮"
            render[1] = "│" + query + " " * (w - 2 - len(query)) + "│"
            render[2] = "╰" + "─" * (w - 2) + "╯"
            
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, ''.join(row), color_pair(DEFAULT))
                
            # Cursor
            stdscr.addstr(1, cursor_position + 1, '│', color_pair(CURSOR))
        except:
            print(f'Could not render!')

    def handle_key(self, ch: int, stdscr: window):
        if ch in ALLOWED:
            self.query += chr(ch)
            self.cursor_position += 1
        elif ch == ESC:
            self.query = ""
            self.app.props['keylock'] = False
            self.app.navigate(self.app.props['last_screen'])
            self.cursor_position = 0
        elif ch == KEY_BACKSPACE:
            if len(self.query) > 0:
                self.cursor_position -= 1
            self.query = self.query[:-1]
        return True
    
    def on_navigate(self):
        self.app.props['keylock'] = True
        self.app.props['keybinds'] = '[esc] Back'
