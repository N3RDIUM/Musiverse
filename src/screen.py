from curses import window


class Screen:
    def __init__(self, app) -> None:
        """
        # creen base class
        """
        self.app = app

    def _render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render the screen

        This renders the screen.

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        self.render(stdscr, frame, frame_rate)

    def _handle_key(self, ch: int) -> None:
        """
        ## Handle a key press

        Called by keyboard_handler.KeyboardHandler

        Arguments:
        - ch: The key pressed
        """
        self.handle_key(ch)

    def _on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        self.on_navigate()
