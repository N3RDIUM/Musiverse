from theme import DEFAULT, CURSOR, SELECTED
from screen import Screen
from curses import window, color_pair, KEY_BACKSPACE, KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, KEY_ENTER
from curses.ascii import ESC, DEL
from multiprocessing import Process, Manager
from os import makedirs, listdir
from os.path import join
from config import config
from thefuzz import fuzz
from time import time, sleep
from json import load
makedirs(config['data_dir'], exist_ok=True)


_allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_.[](){}'\"<>?/\\|!@#$%^&*=+`~"
ALLOWED = set([ord(i) for i in _allowed])

class Result:
    def __init__(self, jsonfile):
        with open(jsonfile, 'r') as f:
            result = load(f)
        self.result = result
        
    def render(self, max_length):
        title = self.result['name']
        return title[:max_length - 4] + '' if len(title) > max_length else title

class Library(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_position = 0
        self.view_position = 0
        self.select = 0
        
    def start_search(self):
        self.manager = Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.query = ""
        self.namespace.last_query = ""
        self.namespace.results = []
        self.process = Process(target=self.search, args=(self.namespace,))
        self.process.start()
    
    def terminate_search(self):
        self.manager.shutdown()
        self.process.terminate()
        self.process.kill()
        self.process.join()
        
    def search(self, namespace):
        while True:
            query = namespace.query
            _query = query
            if query == "":
                try:
                    results = listdir(config['data_dir'])
                    results = [Result(join(config['data_dir'], result)) for result in results]
                    results = sorted(results, key=lambda x: x.result['name'], reverse=True)
                    results = results[:config['max_search_results']]
                    namespace.last_query = namespace.query
                    namespace.results = results
                except Exception as e: print(e)
            if query == namespace.last_query:
                continue
            try:
                results = listdir(config['data_dir'])
                results = [Result(join(config['data_dir'], result)) for result in results]
                results = sorted(results, key=lambda x: fuzz.ratio(x.result['name'], _query), reverse=True)
                results = results[:config['max_search_results']]
                namespace.last_query = namespace.query
                namespace.results = results
            except Exception as e: print(e)
            sleep(config['search_interval'])

    def render(self, stdscr: window, frame: int, frame_rate: float):
        h, w = stdscr.getmaxyx()
        h -= self.app.props['statusbar'].height
        render = [' ' * w for _ in range(h)]
        
        # Render the thing
        try:
            query = self.namespace.query[self.view_position : self.view_position + w - 2]
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
            
            for x, row in enumerate(render):
                stdscr.addstr(x, 0, ''.join(row), color_pair(DEFAULT))
                
            for i, result in enumerate(self.namespace.results):
                if i + self.view_position >= h - self.app.props['statusbar'].height:
                    break
                rendered = result.render(w - 3)
                pair = SELECTED if i == self.select else DEFAULT
                cursor = " " if i != self.select else ("" if time() % config['cursor_blink_rate'] < 0.5 else " ")
                stdscr.addstr(i + 3, 1, cursor + " " + rendered +  " " * (w - 4 - len(rendered)), color_pair(pair))
                if i == self.select: self.app.props['library_selected'] = result
            
            if len(self.namespace.results) == 0:
                nothing = "Search something!"
                icon = "󰍉"
                stdscr.addstr(3, 1, " " * (w - 1 - len(nothing)) + nothing, color_pair(DEFAULT))
                stdscr.addstr(1, w - 3, icon, color_pair(DEFAULT))
                
            # Cursor
            stdscr.addstr(1, cursor_position + 1, ("│" if (time() + 0.5) % config['cursor_blink_rate'] < 0.5 else " "), color_pair(CURSOR))
        except:
            print(f'Could not render!')

    def handle_key(self, ch: int, stdscr: window):
        if ch in ALLOWED:
            self.namespace.query = self.namespace.query[:self.cursor_position] + chr(ch) + self.namespace.query[self.cursor_position:]
            self.cursor_position += 1
        elif ch == ESC:
            self.terminate_search()
            self.app.props['keylock'] = False
            self.app.navigate(self.app.props['last_screen'])
            self.cursor_position = 0
        elif ch == KEY_BACKSPACE: # TODO: DEL KEY
            if len(self.namespace.query) > 0:
                self.cursor_position -= 1
            self.namespace.query = self.namespace.query[0 : self.cursor_position] + self.namespace.query[self.cursor_position + 1 :]
        elif ch == KEY_RIGHT:
            self.cursor_position += 1
        elif ch == KEY_LEFT:
            self.cursor_position -= 1
        elif ch == KEY_UP:
            self.select -= 1
            if self.select < 0:
                self.select = len(self.namespace.results) - 1
        elif ch == KEY_DOWN:
            self.select += 1
            if self.select >= len(self.namespace.results):
                self.select = 0
        elif ch == KEY_ENTER:
            pass # Create playlist if it doesn't exist
        return True
    
    def on_navigate(self):
        self.app.props['keylock'] = True
        self.app.props['keybinds'] = '[󱊷] Back [󰌑] Download'
        self.start_search()
