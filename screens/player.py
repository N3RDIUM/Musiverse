from curses import color_pair, window, KEY_LEFT, KEY_RIGHT

import pygame

from do_nothing import do_nothing
from screen import Screen
from theme import DEFAULT
from time import sleep
from threading import Thread
from config import config
from json import load
from song import Song
from random import randint

# Unique enough ;)
SONG_END = 69


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
            "song": None,
        }
        self.offset = 0
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
                progress = (pygame.mixer.music.get_pos() - self.offset) / 1000
                self.app.props["playing"]["progress"] = int(progress / length * 100)
            except Exception:
                pass
            sleep(config["progress_update_interval"])

    def update_player(self) -> None:
        while True:
            try:
                if self.app.props["playing"]["song"] is None:
                    self.no_song()
                    raise Exception  # Jump to the sleeping part

                if str(self.player_status["song"]) != str(
                    self.app.props["playing"]["song"]
                ):
                    self.player_status["song"] = self.app.props["playing"]["song"]
                    try:
                        filename = self.player_status["song"]["file"]
                        title = self.player_status["song"]["title"]
                        self.play(filename, title)
                    except Exception as e:
                        self.app.props["status_text"] = f"Could not play: {e}"

                if (
                    pygame.mixer.music.get_endevent() == SONG_END
                    and not pygame.mixer.music.get_busy()
                ):
                    self.handle_next()
            except Exception as e:
                self.app.props["status_text"] = f"Could not play: {e}"

            finally:
                sleep(config["progress_update_interval"])

    def no_song(self) -> None:
        """
        ## No song playing

        Called when no song is playing
        """
        pygame.mixer.music.set_endevent(0)
        pygame.mixer.music.stop()
        self.app.props["playing"]["status"]["playing"] = False
        self.app.props["playing"]["song"] = None
        self.app.props["playing"]["progress"] = 0
        self.offset = 0

    def play(self, filename, title):
        self.app.props["status_text"] = f"Now Playing: {title}"

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()

        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_endevent(SONG_END)
        pygame.mixer.music.play(loops=0, start=0)
        pygame.mixer.music.set_volume(1)

        self.sound = pygame.mixer.Sound(filename)

    def handle_next(self) -> None:
        """
        ## Handle next song

        Called when the player reaches the end of the song
        """
        player_status = self.app.props["playing"]["status"]
        if player_status["loop"]:
            match player_status["loop_type"]:
                case "single":
                    self.handle_loop_single()
                case "all":
                    self.handle_loop_all()

    def handle_loop_single(self) -> None:
        """
        ## Handle loop single

        Called when the player reaches the end of the song
        """
        pygame.mixer.music.rewind()
        pygame.mixer.music.play(loops=0, start=0)
        title = self.player_status["song"]["title"]
        self.app.props["status_text"] = f"On Loop: {title}"

    def handle_loop_all(self) -> None:
        """
        ## Handle loop all

        Called when the player reaches the end of the song
        """
        self.no_song()
        song_id = self.player_status["song"]["id"]
        playlist = self.app.props["playlist"]
        with open(playlist) as f:
            playlist = load(f)
        index = playlist["songs"].index(song_id)
        player_status = self.app.props["playing"]["status"]
        match player_status["shuffle"]:
            case False:
                if index == len(playlist["songs"]) - 1:
                    self.app.props["playing"]["song"] = Song(playlist["songs"][0]).data
                else:
                    self.app.props["playing"]["song"] = Song(
                        playlist["songs"][index + 1]
                    ).data
                title = self.player_status["song"]["title"]
                self.app.props["status_text"] = f"On Playlist Loop: {title}"
            case True:  # TODO! Shuffle without loop
                self.app.props["playing"]["song"] = Song(
                    playlist["songs"][randint(0, len(playlist["songs"]) - 1)]
                ).data

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

    def handle_key_bg(self, ch: int) -> None:
        """
        ## Handle a key press when the screen is not active

        Called by keyboard_handler.KeyboardHandler

        Arguments:
        - ch: The key pressed
        """
        if ch == ord("z"):
            try:
                self.offset = pygame.mixer.music.get_pos()
                pygame.mixer.music.rewind()
            except pygame.error:
                self.app.props["status_text"] = "No song playing!"
                self.no_song()
        elif ch == ord("m"):
            try:
                self.offset = 0
                pygame.mixer.music.set_pos(self.sound.get_length() * 1000 - 1)
            except pygame.error:
                self.app.props["status_text"] = "No song playing!"
                self.no_song()

        if ch == KEY_LEFT:
            try:
                pygame.mixer.music.rewind()
                current = (
                    pygame.mixer.music.get_pos() - self.offset - config["seek_interval"]
                )
                pygame.mixer.music.set_pos(current / 1000)
                self.offset += 1000
            except pygame.error:
                self.app.props["status_text"] = "No song playing!"
                self.no_song()
        elif ch == KEY_RIGHT:
            try:
                pygame.mixer.music.rewind()
                current = (
                    pygame.mixer.music.get_pos() - self.offset - config["seek_interval"]
                )
                pygame.mixer.music.set_pos(current / 1000)
                self.offset -= 1000
            except pygame.error:
                self.app.props["status_text"] = "No song playing!"
                self.no_song()

    def on_navigate(self) -> None:
        """
        ## On navigate

        Called by app.App when the user navigates to this screen
        """
        return None
