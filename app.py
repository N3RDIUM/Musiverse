from curses import window

from screen import Screen
from storage import Storage


class App:
    def __init__(self) -> None:
        """
        # App

        The main application class.
        It handles screens, navigation, keybinds,
        local data storage with `storage.py`,
        and lets screens communicate with each other via `props`.
        """
        self.current = None
        self.screens = {}
        self.props = {
            "keybinds": "[Q]uit",
            "keylock": False,
            "status_text": "",
            "queue": [],
            "selected": [],
            "playlist": None,
            "playing": {
                "status": {
                    "playing": False,
                    "loop": False,
                    "loop_type": "single",  # or all
                    "shuffle": False,
                },
                "song": None,
                "progress": 42,
            },
        }
        self.storage = Storage(self)

    def add_screen(self, name: str, screen: Screen) -> None:
        """
        ## Add a screen

        Arguments:
        - name: The name of the screen
        - screen: The screen to add
        """
        self.screens[name] = screen
        if not self.current:
            self.current = name

    def navigate(self, name: str) -> None:
        """
        ## Navigate

        Arguments:
        - name: The name of the screen to navigate to
        """
        self.props["last_screen"] = self.current
        self.current = name
        try:
            self.screens[self.current].on_navigate()
        except AttributeError:
            pass

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        try:
            return self.screens[self.current].render(stdscr, frame, frame_rate)
        except KeyError:
            raise KeyError(f"Unknown screen: {self.current}")

    def on_kill(self) -> None:
        """
        ## On kill

        This is called by KeyboardHandler when the app is killed.
        """
        try:
            self.screens[self.current].on_kill()
        except AttributeError:
            pass
        self.storage.kill()
