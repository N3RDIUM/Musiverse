from json import load
from os.path import exists, join

from config import config


class Song:
    def __init__(self, id) -> None:
        """
        # Song

        This class holds data about a song.
        It auto-loads the data from a json file.
        """
        self.file = join(config["index_dir"], f"{id}.json")
        if exists(self.file):
            with open(self.file) as f:
                self.data = load(f)
        else:
            raise Exception(f"Song not found: {id}")

    def render(self, max_length) -> str:
        """
        # Render

        Renders the title of the song for display.
        """
        title = self.data["title"]
        return title[: max_length - 4] + "" if len(title) > max_length else title

    @property
    def audiofile(self) -> str:
        return self.data["file"]
