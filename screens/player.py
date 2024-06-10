from curses import color_pair, window

import pygame

from do_nothing import do_nothing
from screen import Screen
from theme import DEFAULT
from time import sleep
from threading import Thread
from config import config

# Unique enough ;)
SONG_END = 69420


class Player(Screen):
    def __init__(self, *args, **kwargs) -> None:
        """
        # The Musiverse Player screen

        Work In Progress!
        """
        super().__init__(*args, **kwargs)
        pygame.mixer.init()
        self.sound = None
        self.player_status = {
            "status": {
                "playing": False,
                "loop": False,
                "loop_type": "single",  # or single
                "shuffle": False,
            },
            "song": None,
        }
        self.progress_thread = Thread(target=self.update_progress)
        self.player_thread = Thread(target=self.update_player)
        self.progress_thread.start()
        self.player_thread.start()

    def update_progress(self) -> None:
        """
        ## Update the player progress

        This function updates the player progress every second.
        """
        while True:
            try:
                length = self.sound.get_length()
                progress = pygame.mixer.music.get_pos() / 1000
                self.app.props["playing"]["progress"] = int(progress / length * 100)
            except Exception:
                pass
            sleep(config["progress_update_interval"])

    def update_player(self) -> None:
        while True:
            if self.player_status["song"] != self.app.props["playing"]["song"]:
                self.player_status["song"] = self.app.props["playing"]["song"]
                try:
                    filename = self.player_status["song"]["file"]
                    title = self.player_status["song"]["title"]
                    self.app.props["status_text"] = f"Now Playing: {title}"

                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.set_endevent(SONG_END)
                    pygame.mixer.music.play(loops=0, start=0)
                    pygame.mixer.music.set_volume(1)

                    self.sound = pygame.mixer.Sound(filename)
                except Exception as e:
                    self.app.props["status_text"] = f"Could not play: {e}"

            if pygame.mixer.music.get_endevent() == SONG_END:
                if (
                    self.app.props["playing"]["loop"]
                    and self.app.props["playing"]["loop_type"] == "single"
                ):
                    pygame.mixer.music.play(loops=0, start=0)
                else:
                    self.app.props["playing"]["status"]["playing"] = False

            sleep(config["progress_update_interval"])

    def render(self, stdscr: window, frame: int, frame_rate: float) -> None:
        """
        ## Render the screen

        This renders the player screen.

        Arguments:
        - stdscr: The curses window
        - frame: The current frame number [DEPRECATED]
        - frame_rate: The current frame rate [DEPRECATED]
        """
        height, width = stdscr.getmaxyx()
        height -= self.app.props["statusbar"].height
        render = [" " * width for _ in range(height)]
        self.app.props["keybinds"] = ""
        do_nothing(frame, frame_rate)

        # Render literally nothing
        try:
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, row, color_pair(DEFAULT))
        except Exception as e:
            print(f"Could not render: {e}")

    def handle_key(self, ch: int) -> None:
        """
        ## Handle a key press

        Called by keyboard_handler.KeyboardHandler

        Arguments:
        - ch: The key pressed
        """
        return ch  # No need for now

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        return None
