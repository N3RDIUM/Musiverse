from curses import color_pair, window

from app import App
from do_nothing import do_nothing
from theme import BUTTON, DISABLED, ENABLED, STATUSBAR

# Icons
PLAY = ""
PAUSE = ""
STOP = ""
NEXT = ""
PREV = ""
REW = ""
FF = ""
SHUFFLE = ""
LOOP = ""

# Progress bar stuff
FILLED = "━"
EMPTY = " "
DELIM = "﹝﹞"


class StatusBar:
    def __init__(self, app: App) -> None:
        """
        # StatusBar

        This class renders the statusbar at the bottom of the screen.

        Arguments:
        - app: The app instance
        """
        self.app = app
        self.height = 4
        app.props["statusbar"] = self

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        height, width = stdscr.getmaxyx()
        do_nothing(frame, frame_rate)
        # TODO! Add constant vars for all magic numbers

        # Render progressbar
        progress = self.app.props["playing"]["progress"]
        stdscr.addstr(
            height - 4,
            0,
            f"{DELIM[0]}{FILLED * int(progress / 100 * (width - 4))}"
            + f"{EMPTY * ((width - 4) - int(progress / 100 * (width - 4)))}{DELIM[1]}",
            color_pair(STATUSBAR),
        )

        stdscr.addstr(
            height - 3,
            0,
            " " * width,
            color_pair(STATUSBAR),
        )
        stdscr.addstr(
            height - 2,
            0,
            " " * width,
            color_pair(STATUSBAR),
        )

        # Song name, play/pause
        song = self.app.props["playing"]["song"]
        song_name = "Nothing Playing"
        if song is not None:
            song_name = song["title"]

        if len(song_name) > width - 8:
            song_name = song_name[0 : width - 8] + ""

        playpause_icon = PAUSE
        if self.app.props["playing"]["status"]["playing"]:
            playpause_icon = PLAY

        stdscr.addstr(
            height - 3,
            int((width - len(song_name)) / 2),
            f"{playpause_icon} {song_name}",
            color_pair(STATUSBAR),
        )

        # Other player stuff
        # Left side: rewind, prev
        stdscr.addstr(
            height - 2,
            1,
            PREV,
            color_pair(BUTTON),
        )
        stdscr.addstr(
            height - 2,
            4,
            REW,
            color_pair(BUTTON),
        )

        # Right side: ff, next
        stdscr.addstr(
            height - 2,
            width - 2,
            NEXT,
            color_pair(BUTTON),
        )
        stdscr.addstr(
            height - 2,
            width - 5,
            FF,
            color_pair(BUTTON),
        )

        pair = [DISABLED, ENABLED][self.app.props["playing"]["status"]["shuffle"]]
        stdscr.addstr(
            height - 2,
            width // 2 - 4,
            SHUFFLE,
            color_pair(pair),
        )

        stdscr.addstr(
            height - 2,
            width // 2,
            STOP,
            color_pair(BUTTON),
        )

        pair = [DISABLED, ENABLED][self.app.props["playing"]["status"]["loop"]]
        loop_suffix = (
            " *" if self.app.props["playing"]["status"]["loop_type"] == "all" else " 1"
        )
        stdscr.addstr(
            height - 2,
            width // 2 + 3,
            LOOP + loop_suffix,
            color_pair(pair),
        )

        # Render active keybinds
        kb = self.app.props["keybinds"]
        lt = self.app.props["status_text"]
        if len(lt) > width - len(kb) - 4:
            lt = lt[0 : width - len(kb) - 4] + "..."

        stdscr.addstr(
            height - 1,
            0,
            lt + " " * (width - len(kb) - len(lt)) + kb,
            color_pair(STATUSBAR),
        )
