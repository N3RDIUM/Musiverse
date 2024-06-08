from curses import window


class Screen:
    def __init__(self, app) -> None:
        self.app = app

    def _render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        self.render(stdscr, frame, frame_rate)

    def handle_key(self, ch: int) -> None:
        raise NotImplementedError("This function/method is not implemented yet.")

    def on_navigate(self) -> None:
        raise NotImplementedError("This function/method is not implemented yet.")
