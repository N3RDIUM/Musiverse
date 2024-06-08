from curses import cbreak, curs_set, nocbreak, start_color, wrapper
from time import perf_counter, sleep

from app import App
from config import config
from keyboard_handler import KeyboardHandler
from screens import Home, Library, Player, Search
from statusbar import StatusBar
from theme import reload_theme

# Create the app, statusbar and keyboard handler
app = App()
statusbar = StatusBar(app)
handler = KeyboardHandler(app)

# Add screens
app.add_screen("home", Home(app))
app.add_screen("search", Search(app))
app.add_screen("library", Library(app))
app.add_screen("player", Player(app))

# Main loop
frame = 0
frame_rate = 60


def main(stdscr):
    global frame
    global frame_rate
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
                statusbar.render(stdscr, frame, frame_rate)
                app.render(stdscr, frame, frame_rate)
            except UnboundLocalError:
                pass

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
