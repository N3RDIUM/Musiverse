from json import dump
from multiprocessing import Manager, Process
from os.path import exists, join

from config import config


class loggerOutputs:  # Shush, yt-dlp!
    def error(msg):
        pass

    def warning(msg):
        pass

    def debug(msg):
        pass


class Storage:
    def __init__(self, app) -> None:
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
        from json import load
        from os import listdir, makedirs
        from os.path import abspath
        from shutil import move
        from threading import Thread

        makedirs(config["download_dir"], exist_ok=True)
        makedirs(config["index_dir"], exist_ok=True)
        makedirs(config["data_dir"], exist_ok=True)

        def download_audio(id) -> str:
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
            makedirs(config["download_dir"], exist_ok=True)
            outfile = join(config["download_dir"], f"{id}.mp3")
            if exists(outfile):
                return outfile
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])
            move(f"{id}.mp3", outfile)
            return outfile

        def update_index_playlist() -> None:
            indexes = listdir(config["index_dir"])
            songs = []
            for file in indexes:
                with open(join(config["index_dir"], file)) as f:
                    songs.append(load(f)["id"])
            with open(join(config["data_dir"], "index.json"), "w") as f:
                dump({"name": "All Songs", "songs": songs}, f)

        def do_it(item, namespace) -> None:
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
                    if item in namespace.doing:
                        continue
                    if item in namespace.done:
                        namespace.queue.remove(item)
                        namespace.doing.remove(item)
                        namespace.queue.pop(0)
                        continue
                    namespace.doing.append(item)
                    thread = Thread(target=do_it, args=(item, namespace))
                    thread.daemon = False
                    thread.start()
                    break
            except Exception as e:
                print(e)

    def kill(self) -> None:
        self.manager.shutdown()
        self.process.terminate()
        self.process.kill()
        self.process.join()

    def update_namespace(self) -> None:
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
