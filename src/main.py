from curses import wrapper

from renderer import Renderer

renderer = Renderer()

wrapper(renderer.mainloop)
