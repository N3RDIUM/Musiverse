from curses import KEY_ENTER, set_escdelay, window
from curses.ascii import ESC
from sys import exit as sys_exit

from app import App


class KeyboardHandler:
    def __init__(self, app: App) -> None:
        self.app = app
        set_escdelay(1)

    def handle(self, stdscr: window) -> None:
        ch = stdscr.getch()

        if ch == 27:
            newch = stdscr.getch()
            if newch == -1:
                ch = ESC
        elif ch == KEY_ENTER or ch == 10 or ch == 13:
            ch = KEY_ENTER

        try:
            self.app.screens[self.app.current].handle_key(ch, stdscr)
        except AttributeError:
            pass

        if self.app.props["keylock"]:
            return

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
