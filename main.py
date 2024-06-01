from curses import wrapper, cbreak, nocbreak
from time import sleep, perf_counter

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
            
            h, w = stdscr.getmaxyx()
            for i in range(h):
                for j in range(w - 1):
                    stdscr.addstr(i, j, str(frame)[-1])
            frame += 1

            stdscr.refresh()
            ch = stdscr.getch()
            
            tock = perf_counter()
            sleep(max(0, 1 / 69 - (tock - tick)))
        except KeyboardInterrupt:
            nocbreak()

wrapper(main)