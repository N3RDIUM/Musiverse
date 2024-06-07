from theme import DEFAULT
from screen import Screen
from curses import window, color_pair

class Player(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        h -= self.app.props['statusbar'].height
        render = [' ' * w for _ in range(h)]
        self.app.props['keybinds'] = ''
        
        # Render the text
        try:
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, row, color_pair(DEFAULT))
        except:
            print('Could not render!')
            
    def handle_key(self, ch: int, stdscr: window):
        return ch # No need for now
    
    def on_navigate(self):
        self.app.props['library_state'] = {'mode': 'list-playlists'}
