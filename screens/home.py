from curses import color_pair, window

from do_nothing import do_nothing
from screen import Screen
from theme import DEFAULT

HOME_TEXT = r"""╭─────────────────────────────────╮
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

HOME_WIDTH, HOME_HEIGHT = len(HOME_TEXT[0]), len(HOME_TEXT)


class Home(Screen):
    def __init__(self, *args, **kwargs) -> None:
        """
        # The Musiverse Home screen

        For now, it's just a static text display.
        """
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render the screen

        This renders the home screen.

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        height, width = stdscr.getmaxyx()
        height -= self.app.props["statusbar"].height
        do_nothing(frame, frame_rate)

        # Set some empty stuff
        render = [[" "] * width for _ in range(height)]
        self.app.props["keybinds"] = ""

        # Get the top-left corner in order to center the text
        x = width // 2 - HOME_WIDTH // 2
        y = height // 2 - HOME_HEIGHT // 2

        # Render the text
        try:
            # Add the HOME_TEXT string centered to the render
            for i, line in enumerate(HOME_TEXT):
                for j, char in enumerate(line):
                    render[y + i][x + j] = char

            # Convert the array of chars into a string
            _render = []
            for row in render:
                _render.append("".join(row))

            # Add it to the stdscr
            for x, row in enumerate(_render):
                stdscr.addstr(x, 0, row, color_pair(DEFAULT))
        except Exception as e:
            print(f"Could not render: {e}")

    def handle_key(self, ch: int) -> None:
        """
        ## Handle a key press

        Called by keyboard_handler.KeyboardHandler

        Arguments:
        - ch: The key pressed
        """
        do_nothing(ch)

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
