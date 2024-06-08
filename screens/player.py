from curses import color_pair, window

from screen import Screen
from theme import DEFAULT


class Player(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        h -= self.app.props["statusbar"].height
        render = [" " * w for _ in range(h)]
        self.app.props["keybinds"] = ""

        # Render the text
        try:
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, row, color_pair(DEFAULT))
        except Exception as e:
            print(f"Could not render: {e}")

    def handle_key(self, ch: int, stdscr: window):
        return ch  # No need for now

    def on_navigate(self):
        self.app.props["library_state"] = {"mode": "list-playlists"}
