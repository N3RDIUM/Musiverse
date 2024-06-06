from curses import wrapper, cbreak, nocbreak, start_color, curs_set
from time import sleep, perf_counter
from app import App
from screens import Home
from screens import Search
from statusbar import StatusBar
from keyboard_handler import KeyboardHandler
from theme import reload_theme
from config import config

# Create the app, statusbar and keyboard handler
app = App()
statusbar = StatusBar(app)
handler = KeyboardHandler(app)

# Add screens
app.add_screen('home', Home(app))
app.add_screen('search', Search(app))

# Main loop
frame = 0
frame_rate = 60
def main(stdscr):
    global frame
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
            if config['theme_live_reload']:
                reload_theme()
            
            try:
                statusbar.render(stdscr, frame, frame_rate)
                app.render(stdscr, frame, frame_rate)
            except UnboundLocalError: pass
            frame += 1

            stdscr.refresh()
            handler.handle(stdscr)
            
            tock = perf_counter()
            sleep(max(0, 1 / config['max_frame_rate'] - (tock - tick)))
            frame_rate = 1 / (perf_counter() - tick)
        except KeyboardInterrupt:
            nocbreak()

# Driver code
if __name__ == "__main__":
    wrapper(main)
