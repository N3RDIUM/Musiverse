from curses import window


class Screen:
    def __init__(self, app) -> None:
        self.app = app

    def _render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        self.render(stdscr, frame, frame_rate)

    def _handle_key(self, ch: int) -> None:
        self.handle_key(ch)

    def _on_navigate(self) -> None:
        self.on_navigate()
