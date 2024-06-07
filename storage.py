import yt_dlp as youtube_dl
from config import config
from os.path import join, abspath, exists
from os import makedirs
from shutil import move

def download_audio(id):
    yt_url = f"https://www.youtube.com/watch?v={id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': join('./%(id)s.%(ext)s'),
    }
    outfile = join(config['download_dir'], f"{id}.mp3")
    if exists(outfile):
        return outfile
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])
    makedirs(config['download_dir'], exist_ok=True)
    move(f"{id}.mp3", outfile)
    return outfile
