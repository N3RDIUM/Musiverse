from curses import window

class Screen:
    def __init__(self, app):
        self.app = app
        
    def _render(self, stdscr: window, frame: int):
        self.render(stdscr, frame)