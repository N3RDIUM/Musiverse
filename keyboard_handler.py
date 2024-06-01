from sys import exit
from app import App

class KeyboardHandler:
    def __init__(self, app: App):
        self.app = app
        
    def handle(self, ch):
        if ch == 104:
            self.app.navigate('home')
        if ch == 113:
            exit(0)
