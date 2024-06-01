from curses import wrapper, cbreak, nocbreak
from time import sleep, perf_counter
from app import App
from screens import Home

# Create the app
app = App()

# Add screens
app.add_screen('home', Home(app))

# Main loop
frame = 0
def main(stdscr):
    global frame
    
    # Mainloop
    while True:
        try:
            cbreak()
            stdscr.clear()
            stdscr.nodelay(True)
            
            tick = perf_counter()
            
            app.render(stdscr, frame)
            frame += 1

            stdscr.refresh()
            ch = stdscr.getch()
            
            tock = perf_counter()
            sleep(max(0, 1 / 69 - (tock - tick)))
        except KeyboardInterrupt:
            nocbreak()

# Driver code
if __name__ == "__main__":
    wrapper(main)
