from curses import KEY_ENTER, set_escdelay, window
from curses.ascii import ESC
from sys import exit as sys_exit

from app import App


class KeyboardHandler:
    def __init__(self, app: App) -> None:
        """
        # Keyboard handler

        Handles keyboard input for the app.

        Arguments:
        - app: The app instance
        """
        self.app = app
        set_escdelay(1)

    def handle(self, stdscr: window) -> None:
        """
        ## Handle keypress

        Arguments:
        - stdscr: The curses window
        """
        # Get key press
        ch = stdscr.getch()

        # Handle special keys
        if ch == 27:
            newch = stdscr.getch()
            if newch == -1:
                ch = ESC
        elif ch in (KEY_ENTER, 10, 13):
            ch = KEY_ENTER

        # Try to tell the current screen about the key
        try:
            self.app.screens[self.app.current].handle_key(ch)
        except AttributeError:
            pass

        # YOU SHALL NOT PASS
        # if the key lock is on
        # i.e. a screen is taking text input.
        if self.app.props["keylock"]:
            return

        # Try to tell the other screens about the key too
        for screen in self.app.screens:
            if screen == self.app.current:
                continue
            try:
                self.app.screens[screen].handle_key_bg(ch)
            except AttributeError:
                pass

        # Handle keys
        # TODO! Make this configurable
        if ch == ord("h") or ch == ord("H"):
            self.app.navigate("home")
        if ch == ord("s") or ch == ord("S"):
            self.app.navigate("search")
        if ch == ord("l") or ch == ord("L"):
            self.app.navigate("library")
        if ch == ord("p") or ch == ord("P"):
            self.app.navigate("player")
        if ch == ord("q") or ch == ord("Q"):
            self.app.on_kill()
            # skipcq: PYL-R1722
            sys_exit(0)
