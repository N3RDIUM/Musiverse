from json import dump
from multiprocessing import Manager, Process
from os.path import exists, join

from config import config
from do_nothing import do_nothing


class loggerOutputs:  # Shush, yt-dlp!
    def error(*args, **kwargs):
        do_nothing(args, kwargs)

    def warning(*args, **kwargs):
        do_nothing(args, kwargs)

    def debug(*args, **kwargs):
        do_nothing(args, kwargs)


class Storage:
    def __init__(self, app) -> None:
        """
        # Storage

        Handles local data storage with `json`

        Arguments:
        - app: The app instance
        """
        self.app = app
        self.manager = Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.list()
        self.namespace.doing = self.manager.list()
        self.namespace.done = self.manager.list()
        self.process = Process(target=self.downloader, args=(self.namespace,))
        self.process.start()

    @staticmethod
    def downloader(namespace) -> None:
        """
        # Downloader

        The downloader downloads queued songs from YouTube parallely
        using threading and storing them in the `download_dir`.
        """
        from json import load
        from os import listdir
        from os.path import abspath
        from shutil import move
        from threading import Thread

        def download_audio(id) -> str:
            """
            ## Download Audio

            This downloads the audio from YouTube and
            returns the path to the file.

            Arguments:
            - id: The YouTube video id

            Returns:
            - The path to the downloaded file
            """
            import yt_dlp as youtube_dl

            yt_url = f"https://www.youtube.com/watch?v={id}"
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": join("./%(id)s.%(ext)s"),
                "logger": loggerOutputs,
            }
            outfile = join(config["download_dir"], f"{id}.mp3")
            if exists(outfile):
                return outfile
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])
            move(f"{id}.mp3", outfile)
            return outfile

        def update_index_playlist() -> None:
            """
            ## Update Index Playlist

            This updates the index playlist.
            The index playlist is a list of all songs in the library.
            It displays as "All Songs" in the library screen.
            """
            indexes = listdir(config["index_dir"])
            songs = []
            for file in indexes:
                with open(join(config["index_dir"], file)) as f:
                    songs.append(load(f)["id"])
            with open(join(config["data_dir"], "index.json"), "w") as f:
                dump({"name": "All Songs", "songs": songs}, f)

        def do_it(item, namespace) -> None:
            """
            ## Do it

            This downloads the audio from YouTube and
            stores it in the `download_dir`.
            Then it updates the index playlist.

            Arguments:
            - item: The item to download
            - namespace: The multiprocessing namespace
            """
            file = download_audio(item["id"])
            item["file"] = abspath(file)
            # skipcq: PTC-W6004
            with open(join(config["index_dir"], f"{item['id']}.json"), "w") as f:
                dump(item, f)
            update_index_playlist()
            namespace.done.append(item)

        while True:
            try:
                for item in namespace.queue:
                    # If this item is already being downloaded
                    # or has already been downloaded, skip it
                    if item in namespace.doing:
                        continue
                    if item in namespace.done:
                        namespace.queue.remove(item)
                        namespace.doing.remove(item)
                        namespace.queue.pop(0)
                        continue

                    # Else, download it
                    namespace.doing.append(item)
                    thread = Thread(target=do_it, args=(item, namespace))
                    thread.daemon = False
                    thread.start()

                    sleep(config["download_thread_interval"])
                    break
            except Exception:
                pass

    def kill(self) -> None:
        """
        ## Kill

        This kills the downloader process.
        """
        self.manager.shutdown()
        self.process.terminate()
        self.process.kill()
        self.process.join()

    def update_namespace(self) -> None:
        """
        ## Update Namespace

        This updates the namespace with the current
        state of the app.
        """
        self.namespace.queue = self.manager.list(self.app.props["queue"])
        for i in self.namespace.done:
            self.app.props["status_text"] = f"Downloaded complete: {i['title']}"
        self.namespace.done = self.manager.list()
        self.app.props["queue"] = list(self.namespace.queue)

    @staticmethod
    def exists(id) -> bool:
        if exists(join(config["index_dir"], f"{id}.json")):
            return True
        return False
