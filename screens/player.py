from curses import color_pair, window

from do_nothing import do_nothing
from screen import Screen
from theme import DEFAULT


class Player(Screen):
    def __init__(self, *args, **kwargs) -> None:
        """
        # The Musiverse Player screen

        Work In Progress!
        """
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render the screen

        This renders the player screen.

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        height, width = stdscr.getmaxyx()
        height -= self.app.props["statusbar"].height
        render = [" " * width for _ in range(height)]
        self.app.props["keybinds"] = ""
        do_nothing(frame, frame_rate)

        # Render literally nothing
        try:
            for x, row in enumerate(render):
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
        return ch  # No need for now

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        return None
