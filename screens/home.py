from screen import Screen
from curses import window

HOME_TEXT = \
"""
╭─────────────────────────────────╮
│        M U S I V E R S E        │
│ (Help me decide a better name!) │
│                                 │
│ H -> Home                       │   
│ Q -> Quit                       │   
╰─────────────────────────────────╯
""".strip().splitlines()

class Home(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int):
        h, w = stdscr.getmaxyx()
        h -= 1 + self.app.props['statusbar'].height
        render = [[' '] * w for _ in range(h)]
        
        # Get width and height of HOME_TEXT
        _w, _h = len(HOME_TEXT[0]), len(HOME_TEXT)
        
        # Center the text
        x = w // 2 - _w // 2
        y = h // 2 - _h // 2
        
        # Render the text
        try:
            for i, line in enumerate(HOME_TEXT):
                for j, char in enumerate(line):
                    render[y + i][x + j] = char
                    
            _render = []
            for row in render:
                _render.append(''.join(row))
            
            for x, row in enumerate(_render):
                stdscr.addstr(x, 0, row)
        except:
            print(f'Minimum window size: {_w}x{_h} chars!')
