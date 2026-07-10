import yt_dlp
import re
import json
import os


def clean_filename(filename: str):
    """Remove all non-alphanumeric characters, make all characters lowercase and use .mp3 extension"""
    stripped = os.path.splitext(filename)[0]
    base = re.sub(r"[^a-zA-Z0-9 ]", "", stripped)
    cleaned = re.sub(r"\s+", "_", base).lower()
    return cleaned


URL = "https://youtu.be/hG1gbOjWWdI?si=46bJTYY6d8t7cI4v"


with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
    info = ydl.extract_info(URL, download=False)

filename = clean_filename(info["title"])

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": filename,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([URL])
