from curses import window
from renderer import Renderer

class App:
    renderer: Renderer

    def __init__(self) -> None:
        self.renderer = Renderer()

    def wrapper(self, stdscr: window) -> None:
        self.renderer.mainloop(stdscr)

