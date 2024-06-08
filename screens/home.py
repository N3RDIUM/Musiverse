from curses import color_pair, window

from screen import Screen
from theme import DEFAULT

HOME_TEXT = """╭─────────────────────────────────╮
│                                 │
│               ___               │
│              /\__\              │
│             /::|  |             │
│            /:|:|  |             │
│           /:/|:|__|__           │
│          /:/ |::::\__\          │
│          \/__/~~/:/  /          │
│                /:/  /           │
│               /:/  /            │
│              /:/  /             │
│              \/__/              │
│                                 │
│        M U S I V E R S E        │
│ (Help me decide a better name!) │
│                                 │
│        H ->         Home        │
│        S ->       Search        │
│        L ->      Library        │
│        P ->       Player        │
│        Q ->         Quit        │
│                                 │
╰─────────────────────────────────╯""".strip().splitlines()


class Home(Screen):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        h, w = stdscr.getmaxyx()
        h -= self.app.props["statusbar"].height
        render = [[" "] * w for _ in range(h)]
        self.app.props["keybinds"] = ""

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
                _render.append("".join(row))

            for x, row in enumerate(_render):
                stdscr.addstr(x, 0, row, color_pair(DEFAULT))
        except Exception as e:
            print(f"Could not render: {e}")

    def handle_key(self, ch: int, stdscr: window) -> None:
        return ch  # No need for now

    def on_navigate(self) -> None:
        pass
