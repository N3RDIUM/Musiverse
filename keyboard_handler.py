from sys import exit
from app import App
from curses import window, set_escdelay, KEY_ENTER
from curses.ascii import ESC

class KeyboardHandler:
    def __init__(self, app: App):
        self.app = app
        set_escdelay(1)
        
    def handle(self, stdscr: window):
        ch = stdscr.getch()
        
        if ch == 27:
            newch = stdscr.getch()
            if newch == -1:
                ch = ESC
        elif ch == KEY_ENTER or ch == 10 or ch == 13:
            ch = KEY_ENTER
        
        try:
            self.app.screens[self.app.current].handle_key(ch, stdscr)
        except AttributeError: pass
        
        if self.app.props['keylock']:
            return
        
        if ch == 104:
            self.app.navigate('home')
        if ch == 115:
            self.app.navigate('search')
        if ch == 113:
            self.app.on_kill()
            exit(0)
