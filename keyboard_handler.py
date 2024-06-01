from sys import exit
from app import App

class KeyboardHandler:
    def __init__(self, app: App):
        self.app = app
        
    def handle(self, ch):
        if 'lock' in self.app.props:
            self.app.screens[self.app.props['lock']].handle(ch)
            return
        if ch == 104:
            self.app.navigate('home')
        if ch == 113:
            exit(0)
