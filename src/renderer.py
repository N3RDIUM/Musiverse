from curses import cbreak, curs_set, endwin, nocbreak, noecho, start_color

BLANK = "+"


class RenderString:
    def __init__(self):
        self.resolution = [42, 42]
        self.strings = []
        self.previous_strings = []

        self.clear()

    def clear(self):
        x, y = self.resolution
        self.strings = [BLANK * x for i in range(y)]

    @property
    def changed(self):
        return True  # TODO

    def swap(self):
        self.previous_strings = self.strings

    def update(self, stdscr):
        resolution = stdscr.getmaxyx()
        self.resolution = [resolution[1], resolution[0]]
        self.clear()


class Renderer:
    def __init__(self):
        self.string = RenderString()
        self.pre_drawcall_hooks = []
        self.post_drawcall_hooks = []
        self.inloop = False
        self.frame_count = 0

    def drawcall(self, stdscr):
        self.string.update(stdscr)

        for hook in self.pre_drawcall_hooks:
            hook()  # TODO: Type check

        if not self.string.changed:
            return

        stdscr.nodelay(True)

        for i in range(len(self.string.strings)):
            string = self.string.strings[i]

            if i == len(self.string.strings) - 1:
                string = string[:-1]  # What?!

            stdscr.addstr(i, 0, string)

        self.frame_count += 1
        stdscr.refresh()

        for hook in self.post_drawcall_hooks:
            hook()  # TODO: Type check

        self.string.swap()
        self.string.clear()

    def mainloop(self, stdscr):
        curs_set(0)
        noecho()
        cbreak()

        if False:
            start_color()
        self.inloop = True

        while self.inloop:
            try:
                self.drawcall(stdscr)
            except Exception:
                break

        nocbreak()
        endwin()
