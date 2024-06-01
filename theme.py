from curses import init_color, init_pair

# Color constants
BACKGROUND = 1
FOREGROUND = 2

# Pairs
DEFAULT    = 1

def theme():
    init_color(BACKGROUND, int(46 / 256 * 1000), int(52 / 256 * 1000), int(64 / 256 * 1000))
    init_color(FOREGROUND, 1000, 1000, 1000)

    init_pair(DEFAULT, FOREGROUND, BACKGROUND)
