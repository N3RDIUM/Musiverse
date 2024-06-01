from curses import wrapper, cbreak, nocbreak, start_color, curs_set
from time import sleep, perf_counter
from app import App
from screens import Home
from statusbar import StatusBar
from keyboard_handler import KeyboardHandler
from theme import theme

# Create the app, statusbar and keyboard handler
app = App()
statusbar = StatusBar(app)
handler = KeyboardHandler(app)

# Add screens
app.add_screen('home', Home(app))

# Main loop
frame = 0
def main(stdscr):
    global frame
    curs_set(False)
    start_color()
    theme()
    
    # Mainloop
    while True:
        try:
            cbreak()
            stdscr.clear()
            stdscr.nodelay(True)
            
            tick = perf_counter()
            
            try:
                app.render(stdscr, frame)
                statusbar.render(stdscr, frame)
            except: print('Render failed!')
            frame += 1

            stdscr.refresh()
            ch = stdscr.getch()
            handler.handle(ch)
            
            tock = perf_counter()
            sleep(max(0, 1 / 69 - (tock - tick)))
        except KeyboardInterrupt:
            nocbreak()

# Driver code
if __name__ == "__main__":
    wrapper(main)
