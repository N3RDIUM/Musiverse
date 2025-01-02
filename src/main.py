from curses import wrapper
from app import App

app = App()
wrapper(app.wrapper)
