from curses import window


class Screen:
    def __init__(self, app):
        self.app = app

    def _render(self, stdscr: window, frame: int, frame_rate: float):
        self.render(stdscr, frame, frame_rate)
