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
from theme import CURSOR, DEFAULT, SELECTED

_allowed = (
    "abcdefghijklmnopqrstuvwxyz"
    + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + "0123456789"
    + " -_.[](){}'\"<>"
    + "?/\\|!@#$%^&*=+`~"
)
ALLOWED = {ord(i) for i in _allowed}


class Result:
    def __init__(self, data) -> None:
        # skipcq: PTC-W6004
        with open(data, "r") as f:
            self.data = load(f)

    def render(self, max_length) -> str:
        name = self.data["name"]
        return name[: max_length - 4] + "" if len(name) > max_length else name


class Library(Screen):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.manager = None
        self.namespace = None
        self.process = None

        self.cursor_position = 0
        self.view_position = 0
        self.select = 0
        self.pos = 0

    def start_search(self) -> None:
        self.manager = Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.query = ""
        self.namespace.results = []
        self.process = Process(target=self.search, args=(self.namespace,))
        self.process.start()

    def terminate_search(self) -> None:
        self.manager.shutdown()
        self.process.terminate()
        self.process.kill()
        self.process.join()

    @staticmethod
    def search(namespace) -> None:
        from thefuzz import process

        while True:
            query = namespace.query
            try:
                results = listdir(config["data_dir"])
                results = [
                    abspath(join(config["data_dir"], result)) for result in results
                ]
                results = [Result(result) for result in results]
                results = sorted(
                    results, key=lambda result: result.data["name"], reverse=True
                )

                if query != "":
                    names = [result.data["name"] for result in results]
                    names_map = {name: i for i, name in enumerate(names)}
                    sort = process.extract(
                        query, names, limit=config["max_search_results"]
                    )
                    results = [results[names_map[result[0]]] for result in sort]

                namespace.results = results
            except Exception as e:
                print(e)
            sleep(config["library_search_interval"])

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        h, w = stdscr.getmaxyx()
        h -= self.app.props["statusbar"].height
        render = [" " * w for _ in range(h)]
        do_nothing(frame, frame_rate)

        # Render the thing
        try:
            query = self.namespace.query[
                self.view_position : self.view_position + w - 2
            ]
            cursor_position = self.cursor_position - self.view_position

            if cursor_position > len(query):
                self.cursor_position = len(query) + self.view_position
            if cursor_position < 1:
                self.cursor_position = 0

            if cursor_position > w - 3:
                self.view_position = len(self.query) - (w - 3)
            if cursor_position == 1 and self.view_position > 0:
                self.view_position -= 1

            render[0] = "╭" + "─" * (w - 2) + "╮"
            render[1] = "│" + query + " " * (w - 2 - len(query)) + "│"
            render[2] = "╰" + "─" * (w - 2) + "╯"

            for x, row in enumerate(render):
                stdscr.addstr(x, 0, "".join(row), color_pair(DEFAULT))
            if self.select > h - self.app.props["statusbar"].height and self.pos < len(
                self.namespace.results
            ):
                self.select = h - self.app.props["statusbar"].height
                self.pos += 1
            if self.select < 1 and self.pos > 0:
                self.select = 1
                self.pos -= 1

            if self.select + self.pos >= len(self.namespace.results):
                self.select -= 1
            if self.select + self.pos < 0:
                self.select += 1

            results = self.namespace.results
            for i, result in enumerate(results):
                i -= self.pos
                if i < 0 or i >= len(results):
                    continue
                if i > h - self.app.props["statusbar"].height:
                    continue
                rendered = result.render(w - 3)
                pair = SELECTED if i == self.select else DEFAULT
                cursor = (
                    " "
                    if i != self.select
                    else ("" if time() % config["cursor_blink_rate"] < 0.5 else " ")
                )
                stdscr.addstr(
                    i + 3,
                    1,
                    cursor + " " + rendered + " " * (w - 4 - len(rendered)),
                    color_pair(pair),
                )

            if len(self.namespace.results) == 0:
                nothing = "Search something!"
                icon = "󰍉"
                stdscr.addstr(
                    3, 1, " " * (w - 1 - len(nothing)) + nothing, color_pair(DEFAULT)
                )
                stdscr.addstr(1, w - 3, icon, color_pair(DEFAULT))

            # Cursor
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
        if ch in ALLOWED:
            self.namespace.query = (
                self.namespace.query[: self.cursor_position]
                + chr(ch)
                + self.namespace.query[self.cursor_position :]
            )
            self.cursor_position += 1
        elif ch == ESC:
            self.terminate_search()
            self.app.props["keylock"] = False
            self.app.navigate(self.app.props["last_screen"])
            self.cursor_position = 0
        elif ch == KEY_BACKSPACE:  # TODO: DEL KEY
            if len(self.namespace.query) > 0:
                self.cursor_position -= 1
            self.namespace.query = (
                self.namespace.query[0 : self.cursor_position]
                + self.namespace.query[self.cursor_position + 1 :]
            )
        elif ch == KEY_RIGHT:
            self.cursor_position += 1
        elif ch == KEY_LEFT:
            self.cursor_position -= 1
        elif ch == KEY_UP:
            self.select -= 1
        elif ch == KEY_DOWN:
            self.select += 1
        elif ch == KEY_ENTER:
            if (
                self.namespace.results[self.select].data["id"]
                not in self.app.props["queue"]
            ):
                self.app.props["status_text"] = self.app.props["status_text"] = (
                    f"Downloading {self.namespace.results[self.select].data['title']}"
                )
                self.app.props["queue"].append(self.namespace.results[self.select].data)
        return True

    def on_navigate(self) -> None:
        self.app.props["keylock"] = True
        self.app.props["keybinds"] = "[󱊷] Back [󰌑] Download"
        self.start_search()
