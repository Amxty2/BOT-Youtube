import os
import time
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from aiogram.types import FSInputFile



class StrictYoutubeDL(YoutubeDL):
    def extract_info(self, url, *args, **kwargs):
        info = super().extract_info(url, *args, **kwargs)
        # Если yt_dlp распознал плейлист или микс
        if info.get('_type') == 'playlist':
            raise DownloadError("Ссылка ведёт на плейлист или микс YouTube, скачивание запрещено")
        return info


def download_mp3_from_youtube(
    url,
    max_duration=600,
    output_folder='downloads'
):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ydl_opts_info = {
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False
    }
    with StrictYoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)

    duration = info.get('duration')
    if int(duration) > max_duration:
        return [f"Видео слишком длинное ({duration} секунд), скачивание отменено."]

    title = info.get('title', 'audio').replace('/', '_').replace('\\', '_')
    mp3_path = os.path.join(output_folder, f"{title}.mp3")

    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, title),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False
    }

    with StrictYoutubeDL(ydl_opts_download) as ydl:
        print("Скачивание...")
        ydl.download([url])
        print("Готово!")

    while not os.path.isfile(mp3_path):
        time.sleep(0.5)

    return [FSInputFile(mp3_path), mp3_path]


def remove_file(path):
    os.remove(path)
