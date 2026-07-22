import logging
import os
import re
from pathlib import Path

from sqlmodel import select
from typing import Any

from yt_dlp import YoutubeDL

from .constants import AUDIO_PATH
from .database import get_session
from .gbox_queue import QueueEntry
from .model import Song

logger = logging.getLogger(__name__)


def clean_filename(filename: str):
    """Remove all non-alphanumeric characters, make all characters lowercase and use .mp3 extension"""
    stripped = os.path.splitext(filename)[0]
    base = re.sub(r"[^a-zA-Z0-9 ]", "", stripped)
    cleaned = re.sub(r"\s+", "_", base).lower()
    return f"{cleaned}.mp3"


def check_if_downloaded(url: str) -> QueueEntry | None:
    """Check if a song is already downloaded"""
    with next(get_session()) as session:
        statement = select(Song).where(Song.url == url)
        song = session.exec(statement).first()
        logger.debug(f"Checking song in database: {song}")

        if song is None:
            return None

        stored_path = Path(song.file_path)
        candidates = [stored_path]
        if not stored_path.is_absolute():
            candidates.insert(0, AUDIO_PATH / stored_path)
        if song.title:
            candidates.append(AUDIO_PATH / f"{song.title}.mp3")

        for candidate in candidates:
            if candidate.is_file():
                resolved_path = str(candidate.resolve())
                if song.file_path != resolved_path:
                    song.file_path = resolved_path
                    session.add(song)
                    session.commit()
                    session.refresh(song)
                return QueueEntry.from_song(song)

        return None


def download_song(url: str, username: str) -> QueueEntry:
    """Download the song from the provided url and enter the download into the database"""

    # check if the song is already downloaded
    if song := check_if_downloaded(url):
        logger.info(f"URL is saved in database: {song}")
        return song
    logger.info(f"URL is not saved in database: {url}")

    # options for downloading the song
    ydl_opts: dict[str, Any] = {
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
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

        # Capture raw metadata variables
        video_id = info_dict.get("id")
        title = info_dict.get("title")
        uploader = info_dict.get("uploader")
        duration = info_dict.get("duration")  # in seconds
        view_count = info_dict.get("view_count")

        if duration is None or duration > 900:
            logger.info("Video is over 15 minutes")
            raise Exception("Video must be less than 15 minutes")

        cleaned_filepath = AUDIO_PATH / clean_filename(f"{title or video_id}.mp3")
        ydl.params["outtmpl"] = {
            "default": str(cleaned_filepath.with_suffix(".%(ext)s"))
        }
        ydl.download([url])

        # Determine the final downloaded file path
        # yt-dlp gives us the template path, we replace the extension with our target (mp3)
        final_filepath = str(cleaned_filepath.resolve())

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
            username=username,
        )

        session.add(new_song)
        session.commit()
        session.refresh(new_song)

        return QueueEntry.from_song(new_song)
