import os
import re
import yt_dlp

from sqlmodel import select

from .constants import AUDIO_PATH
from .database import get_session
from .model import Song


def clean_filename(filename: str):
    """Remove all non-alphanumeric characters, make all characters lowercase and use .mp3 extension"""
    stripped = os.path.splitext(filename)[0]
    base = re.sub(r"[^a-zA-Z0-9 ]", "", stripped)
    cleaned = re.sub(r"\s+", "_", base).lower()
    return f"{cleaned}.mp3"


def check_if_downloaded(url: str):
    """Check if a song is already downloaded"""
    with next(get_session()) as session:
        statement = select(Song).where(Song.url == url)
        result = session.exec(statement).first()

        return result


def download_song(url: str) -> Song:
    """Download the song from the provided url and enter the download into the database"""

    # check if the song is already downloaded
    if song := check_if_downloaded(url):
        return song

    # options for downloading the song
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            AUDIO_PATH, "%(title)s.%(ext)s"
        ),  # Custom directory template
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    # download the song
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)

        # Capture raw metadata variables
        video_id = info_dict.get("id")
        title = info_dict.get("title")
        uploader = info_dict.get("uploader")
        duration = info_dict.get("duration")  # in seconds
        view_count = info_dict.get("view_count")

        # Determine the final downloaded file path
        # yt-dlp gives us the template path, we replace the extension with our target (mp3)
        temp_filepath = ydl.prepare_filename(info_dict)
        final_filepath = clean_filename(os.path.basename(temp_filepath))

    # create an entry for the song in the database
    with next(get_session()) as session:
        new_song = Song(
            url=url,
            video_id=video_id,
            title=title,
            uploader=uploader,
            duration=duration,
            view_count=view_count,
            file_path=final_filepath,
        )

        session.add(new_song)
        session.commit()

        return new_song
