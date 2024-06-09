from screens.home import Home
from screens.search import Search
from screens.library import Library
from screens.player import Player


def add_screens(app) -> None:
    """
    ## Add screens

    This adds the four screens to the app

    Arguments:
    - app: App of type app.App

    Returns:
    - None
    """
    app.add_screen("home", Home(app))
    app.add_screen("search", Search(app))
    app.add_screen("library", Library(app))
    app.add_screen("player", Player(app))
