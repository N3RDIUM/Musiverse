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
        self.namespace.done = self.manager.list()
        self.process = Process(target=self.downloader, args=(self.namespace,))
        self.process.start()

    def downloader(self, namespace) -> None:
        from os import makedirs
        from os.path import abspath, exists, join
        from shutil import move

        import yt_dlp as youtube_dl

        makedirs(config["download_dir"], exist_ok=True)
        makedirs(join(config["download_dir"], "index/"), exist_ok=True)

        def download_audio(id):
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

        while True:
            try:
                item = namespace.queue[0]
                file = download_audio(item["id"])
                item["file"] = abspath(file)
                with open(join(config["index_dir"], f"{item['id']}.json"), "w") as f:
                    dump(item, f)
                namespace.done.append(item)
                namespace.queue.pop(0)
            except IndexError:
                pass

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

    def exists(self, id: str) -> bool:
        if exists(join(config["index_dir"], f"{id}.json")):
            return True
        return False
