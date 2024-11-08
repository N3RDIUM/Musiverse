import json
from curses import init_color, init_pair
from typing import Tuple

from config import config

# Color constants
BACKGROUND = 1
FOREGROUND = 2
STATUSBARBG = 3
STATUSBARFG = 4
CURSORCOL = 5
SELECTBG = 6
DOWNLOADINGFG = 7
DOWNLOADEDFG = 8
DOWNLOADEDBG = 9
SELECTFG = 10
ENABLEDFG = 11
DISABLEDFG = 12
BUTTONFG = 13
BUTTONBG = 14
PLAYINGFG = 15

# Pairs
DEFAULT = 1
STATUSBAR = 2
CURSOR = 3
SELECT = 4
DOWNLOADING = 5
DOWNLOADED = 6
SELECTED = 7
ENABLED = 8
DISABLED = 9
BUTTON = 10
PLAYING = 11


# Function to process color
def process_color(color_str: str) -> Tuple[int, int, int]:
    color = int(color_str.strip("#"), 16)
    color = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
    return (
        int(color[0] / 256 * 1000),
        int(color[1] / 256 * 1000),
        int(color[2] / 256 * 1000),
    )


# Function to reload the theme
def reload_theme() -> None:
    """
    ## Reload the theme

    This reloads the theme. Should be pretty self-explanatory.
    """
    theme = config["theme"]
    theme = json.load(open(f"themes/{theme}.json"))

    init_color(BACKGROUND, *process_color(theme["background"]))
    init_color(FOREGROUND, *process_color(theme["foreground"]))
    init_color(STATUSBARFG, *process_color(theme["statusbar_foreground"]))
    init_color(STATUSBARBG, *process_color(theme["statusbar_background"]))
    init_color(CURSORCOL, *process_color(theme["cursor"]))
    init_color(SELECTBG, *process_color(theme["select_background"]))
    init_color(DOWNLOADINGFG, *process_color(theme["downloading_foreground"]))
    init_color(DOWNLOADEDFG, *process_color(theme["downloaded_foreground"]))
    init_color(DOWNLOADEDBG, *process_color(theme["downloaded_background"]))
    init_color(SELECTFG, *process_color(theme["selected_foreground"]))
    init_color(ENABLEDFG, *process_color(theme["enabled"]))
    init_color(DISABLEDFG, *process_color(theme["disabled"]))
    init_color(BUTTONFG, *process_color(theme["button_foreground"]))
    init_color(BUTTONBG, *process_color(theme["button_background"]))
    init_color(PLAYINGFG, *process_color(theme["playing_foreground"]))

    init_pair(DEFAULT, FOREGROUND, BACKGROUND)
    init_pair(STATUSBAR, STATUSBARFG, STATUSBARBG)
    init_pair(STATUSBAR, STATUSBARFG, STATUSBARBG)
    init_pair(CURSOR, CURSORCOL, BACKGROUND)
    init_pair(SELECT, FOREGROUND, SELECTBG)
    init_pair(DOWNLOADING, DOWNLOADINGFG, SELECTBG)
    init_pair(DOWNLOADED, DOWNLOADEDFG, DOWNLOADEDBG)
    init_pair(SELECTED, SELECTFG, SELECTBG)
    init_pair(ENABLED, ENABLEDFG, STATUSBARBG)
    init_pair(DISABLED, DISABLEDFG, STATUSBARBG)
    init_pair(BUTTON, BUTTONFG, BUTTONBG)
    init_pair(PLAYING, PLAYINGFG, BACKGROUND)
