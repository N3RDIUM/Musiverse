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
from json import load
from multiprocessing import Manager, Process
from os import listdir
from os.path import abspath, join
from time import sleep, time

from config import config
from do_nothing import do_nothing
from screen import Screen
from song import Song
from theme import CURSOR, DEFAULT, SELECT, SELECTED

# List of allowed characters in the search
_allowed = (
    "abcdefghijklmnopqrstuvwxyz"
    + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + "0123456789"
    + " -_.[](){}'\"<>"
    + "?/\\|!@#$%^&*=+`~"
)
ALLOWED = {ord(i) for i in _allowed}

# Enum of library modes (search and playlist)
LIBRARY_MODES = {"search": 0, "playlist": 1}


class Result:
    def __init__(self, data) -> None:
        """
        # Result

        This class holds data about a playlist.
        It auto-loads the data from a json file.
        """
        self.filename = data
        # skipcq: PTC-W6004
        with open(data, "r") as f:
            self.data = load(f)

    def render(self, max_length) -> str:
        """
        ## Render

        Arguments:
        - max_length: The maximum length of the string to render

        Returns:
        - The rendered string (the name of the playlist)
        """
        name = self.data["name"]
        return name[: max_length - 4] + "" if len(name) > max_length else name


class Library(Screen):
    def __init__(self, *args, **kwargs) -> None:
        """
        # The Musiverse Library screen

        It is a dual-mode screen.
        You can search playlists and view the songs in a playlist.
        Editing playlists is coming soon!
        """
        super().__init__(*args, **kwargs)

        # Initialize empty vars for the search process
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
        It uses fuzzy matching to search for playlists.
        """
        from thefuzz import process

        while True:
            query = namespace.query
            try:
                # Load all playlist info and sort alphabetically
                results = listdir(config["data_dir"])
                results = [
                    abspath(join(config["data_dir"], result)) for result in results
                ]
                results = [Result(result) for result in results]
                results = sorted(
                    results, key=lambda result: result.data["name"], reverse=True
                )

                # If there is a query, use fuzzy matching
                if query != "":
                    names = [result.data["name"] for result in results]
                    names_map = {name: i for i, name in enumerate(names)}
                    sort = process.extract(
                        query, names, limit=config["max_search_results"]
                    )
                    results = [results[names_map[result[0]]] for result in sort]

                # Transfer the results to the main process
                namespace.results = results
            except Exception as e:
                print(e)

            # Sleep for some time between each iteration
            # This is done so that you don't fry your computer.
            sleep(config["library_search_interval"])

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
        height, width = stdscr.getmaxyx()
        height -= self.app.props["statusbar"].height
        render = [" " * width for _ in range(height)]
        do_nothing(frame, frame_rate)

        # Render the thing
        try:
            if self.app.props["library_status"] == LIBRARY_MODES["search"]:
                # Get the slice of the query that will be rendered
                query = self.namespace.query[
                    self.view_position : self.view_position + width - 2
                ]

                # Modify the cursor position based on the view position
                cursor_position = self.cursor_position - self.view_position

                if cursor_position > len(query):
                    self.cursor_position = len(query) + self.view_position
                if cursor_position < 1:
                    self.cursor_position = 0

                if cursor_position > width - 3:
                    self.view_position = len(self.query) - (width - 3)
                if cursor_position == 1 and self.view_position > 0:
                    self.view_position -= 1

                if self.selected > height - self.app.props[
                    "statusbar"
                ].height and self.vertical_position < len(self.namespace.results):
                    self.selected = height - self.app.props["statusbar"].height
                    self.vertical_position += 1
                if self.selected < 1 and self.vertical_position > 0:
                    self.selected = 1
                    self.vertical_position -= 1

                if self.selected + self.vertical_position >= len(
                    self.namespace.results
                ):
                    self.selected -= 1
                if self.selected + self.vertical_position < 0:
                    self.selected += 1

                # Add a nicely boxed query to the render string
                render[0] = "╭" + "─" * (width - 2) + "╮"
                render[1] = "│" + query + " " * (width - 2 - len(query)) + "│"
                render[2] = "╰" + "─" * (width - 2) + "╯"

                # Render the render string
                for x, row in enumerate(render):
                    stdscr.addstr(x, 0, "".join(row), color_pair(DEFAULT))

                # Render the search results
                results = self.namespace.results
                for i, result in enumerate(results):
                    # Index logic
                    i -= self.vertical_position
                    if i < 0 or i >= len(results):
                        continue
                    if i > height - self.app.props["statusbar"].height:
                        continue

                    # Render the result and add its string to the stdscr
                    rendered = result.render(width - 3)
                    pair = (
                        SELECT
                        if i == self.selected + self.vertical_position
                        else DEFAULT
                    )

                    cursor = (
                        " "
                        if i != self.selected + self.vertical_position
                        else (
                            "" if time() % config["cursor_blink_rate"] < 0.5 else " "
                        )
                    )
                    stdscr.addstr(
                        i + 3,
                        1,
                        cursor + " " + rendered + " " * (width - 4 - len(rendered)),
                        color_pair(pair),
                    )

                # Nothing was found
                if len(self.namespace.results) == 0:
                    nothing = "Nothing was found :("
                    icon = "󰍉"
                    stdscr.addstr(
                        3,
                        1,
                        " " * (width - 1 - len(nothing)) + nothing,
                        color_pair(DEFAULT),
                    )
                    stdscr.addstr(1, width - 3, icon, color_pair(DEFAULT))

                # Render the cursor
                stdscr.addstr(
                    1,
                    cursor_position + 1,
                    (
                        "│"
                        if (time() + 0.5) % config["cursor_blink_rate"] < 0.5
                        else " "
                    ),
                    color_pair(CURSOR),
                )

            elif self.app.props["library_status"] == LIBRARY_MODES["playlist"]:
                playlist = self.app.props["playlist"]
                with open(playlist) as f:
                    playlist = load(f)

                # Render the playlist title
                name = f"Playlist: {playlist['name']}"
                render[0] = "╭" + "─" * (width - 2) + "╮"
                render[1] = "│" + name + " " * (width - 2 - len(name)) + "│"
                render[2] = "╰" + "─" * (width - 2) + "╯"

                # The whole screen needs to be rendered with at least whitespaces
                # else the background color won't appear ;-;
                for x, row in enumerate(render):
                    stdscr.addstr(x, 0, "".join(row), color_pair(DEFAULT))

                # Modify the cursor position
                if self.selected > height - self.app.props[
                    "statusbar"
                ].height and self.vertical_position < len(playlist["songs"]):
                    self.selected = height - self.app.props["statusbar"].height
                    self.vertical_position += 1
                if self.selected < 1 and self.vertical_position > 0:
                    self.selected = 1
                    self.vertical_position -= 1

                if self.selected + self.vertical_position >= len(playlist["songs"]):
                    self.selected -= 1
                if self.selected + self.vertical_position < 0:
                    self.selected += 1

                # Render the playlist songs
                songs = playlist["songs"]
                songs = [Song(i) for i in songs]

                for i, song in enumerate(songs):
                    # Index logic
                    i -= self.vertical_position
                    if i < 0 or i >= len(songs):
                        continue
                    if i > height - self.app.props["statusbar"].height:
                        continue

                    # Render the result and add its string to the stdscr
                    rendered = song.render(width - 3)
                    pair = (
                        SELECT
                        if i == self.selected + self.vertical_position
                        else DEFAULT
                    )
                    if song.data in self.app.props["selected"]:
                        pair = SELECTED

                    cursor = (
                        " "
                        if i != self.selected + self.vertical_position
                        else (
                            "" if time() % config["cursor_blink_rate"] < 0.5 else " "
                        )
                    )
                    stdscr.addstr(
                        i + 3,
                        1,
                        cursor + " " + rendered + " " * (width - 4 - len(rendered)),
                        color_pair(pair),
                    )

                # No songs in this playlist :(
                if len(songs) == 0:
                    nothing = "Add some songs!"
                    icon = "󰍉"
                    stdscr.addstr(
                        3,
                        1,
                        " " * (width - 1 - len(nothing)) + nothing,
                        color_pair(DEFAULT),
                    )
                    stdscr.addstr(1, width - 3, icon, color_pair(DEFAULT))

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
        if self.app.props["library_status"] == LIBRARY_MODES["search"]:
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

            # Enter to go into the selected playlist
            elif ch == KEY_ENTER:
                result = self.namespace.results[self.selected + self.vertical_position]
                filename = result.filename
                self.app.props["keylock"] = False
                self.app.props["playlist"] = filename
                self.app.props["library_status"] = LIBRARY_MODES["playlist"]
                self.app.props["keybinds"] = "[󱊷] Back [space] Play [tab] Select"
                self.selected = 0
                self.vertical_position = 0

        elif self.app.props["library_status"] == LIBRARY_MODES["playlist"]:
            # Esc to go back to playlist search
            if ch == ESC:
                self.app.props["keylock"] = True
                self.app.props["keybinds"] = "[󱊷] Back [󰌑] Open [tab] Create playlist"
                self.app.props["library_status"] = LIBRARY_MODES["search"]
                self.selected = 0
                self.vertical_position = 0
            # Cursor movement logic
            elif ch == KEY_UP:
                self.selected -= 1
            elif ch == KEY_DOWN:
                self.selected += 1
            # Enter to start playing
            elif ch == KEY_ENTER:
                pass
            # Selection logic
            elif ch == ord("\t"):
                try:
                    playlist = self.app.props["playlist"]
                    with open(playlist) as f:
                        playlist = load(f)

                    result = Song(
                        playlist["songs"][self.selected + self.vertical_position]
                    )
                    if result.data not in self.app.props["selected"]:
                        self.app.props["selected"].append(result.data)
                    else:
                        self.app.props["selected"].remove(result.data)
                except Exception as e:
                    print(f"Could not select: {e}")
        return True

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        self.app.props["keylock"] = True
        self.app.props["keybinds"] = "[󱊷] Back [󰌑] Open [tab] Create playlist"
        self.app.props["library_status"] = LIBRARY_MODES["search"]
        self.start_search()
