from curses import (
    KEY_BACKSPACE,
    KEY_DOWN,
    KEY_ENTER,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_UP,
    color_pair,
    window,
)
from curses.ascii import ESC  # , DEL
from multiprocessing import Manager, Process
from time import sleep, time

from config import config
from do_nothing import do_nothing
from screen import Screen
from storage import Storage
from json import load
from theme import CURSOR, DEFAULT, DOWNLOADED, DOWNLOADING, SELECT, SELECTED

_allowed = (
    "abcdefghijklmnopqrstuvwxyz"
    + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + "0123456789"
    + " -_.[](){}'\"<>"
    + "?/\\|!@#$%^&*=+`~"
)
ALLOWED = {ord(i) for i in _allowed}


class Result:
    def __init__(self, result) -> None:
        """
        # Result

        This class holds data about a song fetched from YouTube.
        """
        self.data = result

    def render(self, max_length) -> str:
        title = self.data["title"]
        return title[: max_length - 4] + "" if len(title) > max_length else title


class OfflineResult:
    def __init__(self, data) -> None:
        """
        # Offline Result

        This class holds data about a song which is already downloaded.
        It auto-loads the data from a json file.
        """
        self.filename = data
        # skipcq: PTC-W6004
        with open(data, "r") as f:
            # skipcq: PTC-W6004
            self.data = load(f)

    def render(self, max_length) -> str:
        name = self.data["title"]
        return name[: max_length - 4] + "" if len(name) > max_length else name


class Search(Screen):
    def __init__(self, *args, **kwargs) -> None:
        """
        # The Musiverse Search screen

        This screen allows you to search and download music from YouTube.
        """
        super().__init__(*args, **kwargs)

        # Init empty vars for the search process
        self.manager = None
        self.namespace = None
        self.process = None

        # Variables for the cursor position
        self.cursor_position = 0
        self.view_position = 0

        # Variables for the selector position
        self.selected = 0
        self.vertical_position = 0

    def start_search(self) -> None:
        """
        ## Start the search process

        This starts a new process that searches for playlists.
        """
        self.manager = Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.query = ""
        self.namespace.last_query = ""
        self.namespace.results = []
        self.process = Process(target=self.search, args=(self.namespace,))
        self.process.start()

    def terminate_search(self) -> None:
        """
        ## Terminate the search process

        This terminates the search process
        when it is no longer needed.
        """
        self.manager.shutdown()
        self.process.terminate()
        self.process.kill()
        self.process.join()

    @staticmethod
    def search(namespace) -> None:
        """
        ## Search process

        This is the main search function.
        It uses the YouTube API to search for playlists.
        """
        from youtube_search import YoutubeSearch
        from os import listdir
        from os.path import abspath, join

        while True:
            # Get the query and add the search prefix and suffix
            query = namespace.query
            _query = config["search_prefix"] + query + config["search_suffix"]

            # If there is no query, load all song names and sort alphabetically
            if query == "":
                results = listdir(config["index_dir"])
                results = [
                    abspath(join(config["index_dir"], result)) for result in results
                ]
                results = [OfflineResult(result) for result in results]
                results = sorted(
                    results, key=lambda result: result.data["title"], reverse=True
                )
                namespace.results = results
                continue

            # If the query is the same as the last query, skip
            if query == namespace.last_query:
                continue

            # If there is a query, use the YouTube API
            try:
                results = YoutubeSearch(
                    _query, max_results=config["max_search_results"]
                ).to_dict()
                results = [Result(result) for result in results]
                namespace.last_query = namespace.query
                namespace.results = results
            except Exception as e:
                print(e)

            # Wait for the configured search interval
            sleep(config["search_interval"])

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render the screen

        This renders the screen.
        It might get a bit complicated,
        but trust me, its pretty simple.

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        h, w = stdscr.getmaxyx()
        h -= self.app.props["statusbar"].height
        render = [" " * w for _ in range(h)]
        do_nothing(frame, frame_rate)

        # Render the thing
        try:
            # Get the slice of the query that will be rendered
            query = self.namespace.query[
                self.view_position : self.view_position + w - 2
            ]

            # Modify the cursor position
            cursor_position = self.cursor_position - self.view_position

            if cursor_position > len(query):
                self.cursor_position = len(query) + self.view_position
            if cursor_position < 1:
                self.cursor_position = 0

            if cursor_position > w - 3:
                self.view_position = len(self.query) - (w - 3)
            if cursor_position == 1 and self.view_position > 0:
                self.view_position -= 1

            if self.selected > h - self.app.props[
                "statusbar"
            ].height and self.vertical_position < len(self.namespace.results):
                self.selected = h - self.app.props["statusbar"].height
                self.vertical_position += 1
            if self.selected < 1 and self.vertical_position > 0:
                self.selected = 1
                self.vertical_position -= 1

            if self.selected + self.vertical_position >= len(self.namespace.results):
                self.selected -= 1
            if self.selected + self.vertical_position < 0:
                self.selected += 1

            # Add a nicely boxed query to the render
            render[0] = "╭" + "─" * (w - 2) + "╮"
            render[1] = "│" + query + " " * (w - 2 - len(query)) + "│"
            render[2] = "╰" + "─" * (w - 2) + "╯"

            # Render the thing
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, "".join(row), color_pair(DEFAULT))

            # Render the search results
            results = self.namespace.results
            for i, result in enumerate(results):
                # Index logic
                i -= self.vertical_position
                if i < 0 or i >= len(results):
                    continue
                if i > h - self.app.props["statusbar"].height:
                    continue

                # Render the result and add its string to the stdscr
                rendered = result.render(w - 3)
                pair = SELECT if i == self.selected else DEFAULT
                if result.data in self.app.props["queue"]:
                    pair = DOWNLOADING
                if Storage.exists(result.data["id"]):
                    pair = DOWNLOADED
                if result.data in self.app.props["selected"]:
                    pair = SELECTED

                cursor = (
                    " "
                    if i != self.selected
                    else ("" if time() % config["cursor_blink_rate"] < 0.5 else " ")
                )
                stdscr.addstr(
                    i + 3,
                    1,
                    cursor + " " + rendered + " " * (w - 4 - len(rendered)),
                    color_pair(pair),
                )

            # Nothing was found
            if len(self.namespace.results) == 0:
                nothing = "No results :("
                icon = "󰍉"
                stdscr.addstr(
                    3, 1, " " * (w - 1 - len(nothing)) + nothing, color_pair(DEFAULT)
                )
                stdscr.addstr(1, w - 3, icon, color_pair(DEFAULT))

            # Render the cursor
            stdscr.addstr(
                1,
                cursor_position + 1,
                ("│" if (time() + 0.5) % config["cursor_blink_rate"] < 0.5 else " "),
                color_pair(CURSOR),
            )
        except Exception as e:
            print(f"Could not render: {e}")

    def handle_key(
        self,
        ch: int,
    ) -> None:
        """
        ## Handle a key press

        Called by keyboard_handler.KeyboardHandler

        Arguments:
        - ch: The key pressed
        """
        # Typing
        if ch in ALLOWED:
            self.namespace.query = (
                self.namespace.query[: self.cursor_position]
                + chr(ch)
                + self.namespace.query[self.cursor_position :]
            )
            self.cursor_position += 1
        elif ch == KEY_BACKSPACE:  # TODO: DEL KEY
            if len(self.namespace.query) > 0:
                self.cursor_position -= 1
            self.namespace.query = (
                self.namespace.query[0 : self.cursor_position]
                + self.namespace.query[self.cursor_position + 1 :]
            )

        # Return to previous screen on esc
        elif ch == ESC:
            self.terminate_search()
            self.app.props["keylock"] = False
            self.app.navigate("home")
            self.cursor_position = 0

        # Cursor movement logic
        elif ch == KEY_RIGHT:
            self.cursor_position += 1
        elif ch == KEY_LEFT:
            self.cursor_position -= 1
        elif ch == KEY_UP:
            self.selected -= 1
        elif ch == KEY_DOWN:
            self.selected += 1

        # Enter to download the selected item
        elif ch == KEY_ENTER:
            if self.namespace.results[self.selected].data not in self.app.props[
                "queue"
            ] and not Storage.exists(self.namespace.results[self.selected].data["id"]):
                self.app.props["status_text"] = self.app.props["status_text"] = (
                    f"Downloading {self.namespace.results[self.selected].data['title']}"
                )
                self.app.props["queue"].append(
                    self.namespace.results[self.selected].data
                )

        # Selection logic
        elif ch == ord("\t"):
            if self.namespace.results[self.selected].data in self.app.props["queue"]:
                self.app.props["queue"].remove(
                    self.namespace.results[self.selected].data
                )
            else:
                self.app.props["selected"].append(
                    self.namespace.results[self.selected].data
                )

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        self.app.props["keylock"] = True
        self.app.props["keybinds"] = "[󱊷] Back [󰌑] Download [tab] Select"
        self.start_search()
