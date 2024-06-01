from app import App

class KeyboardHandler:
    def __init__(self, app: App):
        self.app = app
        
    def handle(self, ch):
        if ch == ord('h'):
            self.app.navigate('home')
