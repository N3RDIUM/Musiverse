from curses import (
    cbreak,
    curs_set,
    nocbreak,
    start_color,
    wrapper,
    error as curses_error,
)
from time import perf_counter, sleep

from app import App
from config import config
from keyboard_handler import KeyboardHandler
from screens import add_screens
from statusbar import StatusBar
from theme import reload_theme

# Make these dirs if they don't exist
from os import makedirs

makedirs(config["download_dir"], exist_ok=True)
makedirs(config["index_dir"], exist_ok=True)
makedirs(config["data_dir"], exist_ok=True)

# Create the app, statusbar and keyboard handler
app = App()
add_screens(app)
statusbar = StatusBar(app)
handler = KeyboardHandler(app)


# Main loop
def main(stdscr) -> None:
    """
    # Musiverse

    This is the mainloop function called by `wrapper()`
    """
    frame = 0
    frame_rate = 60
    curs_set(0)
    start_color()
    reload_theme()

    # Mainloop
    while True:
        try:
            tick = perf_counter()
            cbreak()
            stdscr.clear()
            stdscr.nodelay(True)

            # TODO! Don't do it this way. Listen for changes instead.
            if config["theme_live_reload"]:
                reload_theme()

            try:
                try:
                    statusbar.render(stdscr, frame, frame_rate)
                except curses_error:  # TODO! Find out why
                    pass
                app.render(stdscr, frame, frame_rate)
            except UnboundLocalError:
                pass
            except curses_error:
                print("Could not render!")

            app.storage.update_namespace()
            frame += 1

            stdscr.refresh()
            handler.handle(stdscr)

            tock = perf_counter()
            sleep(max(0, 1 / config["max_frame_rate"] - (tock - tick)))
            frame_rate = 1 / (perf_counter() - tick)
        except KeyboardInterrupt:
            nocbreak()


# Driver code
if __name__ == "__main__":
    wrapper(main)
