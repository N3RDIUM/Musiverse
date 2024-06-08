from curses import color_pair, curs_set, window

from app import App
from theme import STATUSBAR

FILLED = "━"
EMPTY = " "
DELIM = "﹝﹞"


class StatusBar:
    def __init__(self, app: App):
        self.app = app
        self.height = 4
        app.props["statusbar"] = self

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()

        # Render progressbar
        stdscr.addstr(
            h - 4,
            0,
            f"{DELIM[0]}{FILLED * int(frame % (w - 4))}{EMPTY * ((w - 4) - int(frame % (w - 4)))}{DELIM[1]}",
            color_pair(STATUSBAR),
        )

        frm = f"Frame: {frame} ({frame_rate:.2f} fps)  /        "
        stdscr.addstr(h - 3, 0, frm + " " * (w - len(frm)), color_pair(STATUSBAR))

        # Empty rows
        stdscr.addstr(h - 2, 0, " " * w, color_pair(STATUSBAR))

        # Render active keybinds
        kb = self.app.props["keybinds"]
        lt = self.app.props["status_text"]
        if len(lt) > w - len(kb) - 4:
            lt = lt[0 : w - len(kb) - 4] + "..."
        stdscr.addstr(
            h - 1, 0, lt + " " * (w - len(kb) - len(lt) - 1) + kb, color_pair(STATUSBAR)
        )
