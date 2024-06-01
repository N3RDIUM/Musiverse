from screen import Screen
from curses import window

class Home(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int):
        h, w = stdscr.getmaxyx()
        render = ""
        
        for i in range(h):
            render += ' ' * (w - 1) + '\n'
            
        # Joe render code goes here
        
        for i, row in enumerate(render.splitlines()):
            stdscr.addstr(i, 0, row)