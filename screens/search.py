from theme import DEFAULT, CURSOR
from screen import Screen
from curses import window, color_pair, KEY_BACKSPACE, KEY_RIGHT, KEY_LEFT
from curses.ascii import ESC, DEL
from youtube_search import YoutubeSearch
from threading import Thread
from time import sleep

_allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_ ."
ALLOWED = set([ord(i) for i in _allowed])

class Search(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = ""
        self.last_query = ""
        self.results = []
        self.cursor_position = 0
        self.view_position = 0
        
        self.thread = Thread(target=self.search)
        self.thread.daemon = True
        self.thread.start()
        
    def search(self):
        while True:
            if self.query == "":
                self.results = []
                continue
            if self.query == self.last_query:
                continue
            try:
                self.results = YoutubeSearch(self.query, max_results=100).to_dict()
                self.last_query = self.query
            except:
                pass
            sleep(0.1)

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        h -= self.app.props['statusbar'].height
        render = [' ' * w for _ in range(h)]
        
        # Render the thing
        try:
            query = self.query[self.view_position : self.view_position + w - 2]
            cursor_position = self.cursor_position - self.view_position
            
            if cursor_position > len(query):
                self.cursor_position = len(query) + self.view_position
            if cursor_position < 1:
                self.cursor_position = 0
                
            if cursor_position > w - 3:
                self.view_position = len(self.query) - (w - 3)
            if cursor_position == 1 and self.view_position > 0:
                self.view_position -= 1
            
            render[0] = "╭" + "─" * (w - 2) + "╮"
            render[1] = "│" + query + " " * (w - 2 - len(query)) + "│"
            render[2] = "╰" + "─" * (w - 2) + "╯"
            
            titles = []
            for result in self.results:
                titles.append(result['title'])
                
            for i, title in enumerate(titles):
                if i + self.view_position >= h - self.app.props['statusbar'].height:
                    break
                render[i + 3] = "│" + title + " " * (w - 2 - len(title)) + "│"
            
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, ''.join(row), color_pair(DEFAULT))
                
            # Cursor
            stdscr.addstr(1, cursor_position + 1, '│', color_pair(CURSOR))
        except:
            print(f'Could not render!')

    def handle_key(self, ch: int, stdscr: window):
        if ch in ALLOWED:
            self.query = self.query[:self.cursor_position] + chr(ch) + self.query[self.cursor_position:]
            self.cursor_position += 1
        elif ch == ESC:
            self.query = ""
            self.app.props['keylock'] = False
            self.app.navigate(self.app.props['last_screen'])
            self.cursor_position = 0
        elif ch == KEY_BACKSPACE: # TODO: DEL KEY
            if len(self.query) > 0:
                self.cursor_position -= 1
            self.query = self.query[0 : self.cursor_position] + self.query[self.cursor_position + 1 :]
        elif ch == KEY_RIGHT:
            self.cursor_position += 1
        elif ch == KEY_LEFT:
            self.cursor_position -= 1
        return True
    
    def on_navigate(self):
        self.app.props['keylock'] = True
        self.app.props['keybinds'] = '[esc] Back'
