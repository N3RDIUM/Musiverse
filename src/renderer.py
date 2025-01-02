from curses import window, cbreak, curs_set, endwin, nocbreak, noecho, start_color
from types import LambdaType

blank = "+"


class RenderString:
    resolution: list[int]
    strings: list[str]
    previous_strings: list[str]
    initial_frame: bool

    def __init__(self) -> None:
        self.resolution = [42, 42]
        self.strings = []
        self.previous_strings = []
        self.initial_frame = True

        self.populate()

    def populate(self) -> None:
        x, y = self.resolution
        self.strings = [blank * x for _ in range(y)]
        self.previous_strings = self.strings

    def clear(self) -> None:
        x, y = self.resolution
        self.strings = [blank * x for _ in range(y)]

    def swap(self) -> None:
        self.previous_strings = self.strings

    def update_resolution(self, resolution: list[int]) -> None:
        self.resolution = resolution
        self.populate()

    @property
    def changed(self) -> bool:
        if self.initial_frame:
            self.initial_frame = False
            return True

        if len(self.strings) != len(self.previous_strings):
            raise RuntimeError("The ruddy lengths don' match!")

        for i in range(len(self.strings)):
            string = self.strings[i]
            previous = self.previous_strings[i]

            if string != previous:
                return True

        return False


class Renderer:
    string: RenderString
    pre_drawcall_hooks: list[LambdaType]
    post_drawcall_hooks: list[LambdaType]
    inloop: bool
    frame_count: int
    previous_resolution: list[int]

    def __init__(self):
        self.string = RenderString()
        self.pre_drawcall_hooks = []
        self.post_drawcall_hooks = []
        self.inloop = False
        self.frame_count = 0
        self.previous_resolution = [42, 42]

    def drawcall(self, stdscr: window):
        if list(stdscr.getmaxyx()) != self.previous_resolution:
            resolution = list(stdscr.getmaxyx())
            resolution.reverse()
            self.string.update_resolution(resolution)
            self.previous_resolution = list(stdscr.getmaxyx())
            self.string.initial_frame = True

        for hook in self.pre_drawcall_hooks:
            hook()

        global blank
        blank = str(self.frame_count)[-1]
        self.string.clear()

        debug = str(list(stdscr.getmaxyx()))
        self.string.strings[0] = debug + self.string.strings[0][len(debug) :]

        if not self.string.changed:
            return

        stdscr.nodelay(True)

        # TODO: Only update the area that has changed
        # TODO: on a character level.
        for i in range(len(self.string.strings)):
            string = self.string.strings[i]

            if i == len(self.string.strings) - 1:
                string = string[:-1]  # What?!

            stdscr.addstr(i, 0, string)

        self.frame_count += 1
        stdscr.refresh()

        for hook in self.post_drawcall_hooks:
            hook()

        self.string.swap()

    def mainloop(self, stdscr: window):
        _ = curs_set(0)
        noecho()
        cbreak()

        _ = start_color()
        self.inloop = True

        while self.inloop:
            self.drawcall(stdscr)

        nocbreak()
        endwin()
