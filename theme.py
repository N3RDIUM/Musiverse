import json
from config import config
from curses import init_color, init_pair

# Color constants
BACKGROUND = 1
FOREGROUND = 2

# Pairs
DEFAULT    = 1

# Function to process color
def process_color(color: str):
    color = int(color.strip('#'), 16)
    color = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
    return (int(color[0] / 256 * 1000), int(color[1] / 256 * 1000), int(color[2] / 256 * 1000))

# Function to reload the theme
def reload_theme():
    theme = config['theme']
    theme = json.load(open(f'themes/{theme}.json'))
    
    init_color(BACKGROUND, *process_color(theme['background']))
    init_color(FOREGROUND, *process_color(theme['foreground']))

    init_pair(DEFAULT, FOREGROUND, BACKGROUND)
