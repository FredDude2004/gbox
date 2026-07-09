import os
import subprocess
import re

import yt_dlp

from dataclasses import dataclass

AUDIO_CACHE = []
INDEX = 0
AUDIO_DIRECTORY = "downloads"


@dataclass
class Song:
    name: str
    url: str


def is_downloaded(youtube_url) -> str | None:
    for audio in AUDIO_CACHE:
        if audio.url == youtube_url:
            return audio.name
        else:
            return None


def play_next_audio():
    global INDEX
    audio = AUDIO_CACHE[INDEX]
    if os.path.exists(AUDIO_DIRECTORY / audio.name):
        subprocess.run(["cvlc", "--no-video", f"{audio.name}.mp3"])
    else:
        raise Exception("Error: Audio not found")

    INDEX += 1


def play_audio(youtube_url):
    print(f"looking for url {youtube_url}")
    for sound in AUDIO_CACHE:
        if sound.url == youtube_url:
            if os.path.exists(os.path.abspath(f"{AUDIO_DIRECTORY}/{sound.name}")):
                subprocess.run(
                    ["cvlc", "--play-and-exit", f"{AUDIO_DIRECTORY}/{sound.name}"]
                )
        else:
            raise Exception("Error: Audio not found")


def download_youtube_audio(youtube_url):
    """
    Downloads the best quality audio from a YouTube video and converts it to MP3.
    """
    # Ensure the output directory exists
    if not os.path.exists(AUDIO_DIRECTORY):
        os.makedirs(AUDIO_DIRECTORY)

    cached = is_downloaded(youtube_url)
    if cached:
        return

    # Configuration options for yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(AUDIO_DIRECTORY, "%(title)s.%(ext)s"),
        # Post-processor configurations to convert the audio stream into an MP3
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",  # Options include 192, 256, or 320 kbps
            }
        ],
        # Optional: Suppress excessive terminal outputs, showing only errors or warnings
        "quiet": False,
    }

    try:
        print(f"Initializing download for: {youtube_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            prepared_filename = ydl.prepare_filename(info_dict)
            base, _ = os.path.splitext(prepared_filename)
            original_filename = f"{base}.mp3"
            print(f"original_filename: {original_filename}")

        # rename the file to be friendly to vlc
        base, ext = os.path.splitext(original_filename)
        cleaned_base = re.sub(r"[^a-zA-Z0-9 ]", "", base)
        cleaned_base = re.sub(r"\s+", "_", cleaned_base).lower()
        cleaned = f"{cleaned_base[len(AUDIO_DIRECTORY)::]}{ext}"
        os.rename(
            original_filename,
            f"{AUDIO_DIRECTORY}/{cleaned}",
        )

        # add audio to cache
        AUDIO_CACHE.append(Song(name=cleaned, url=youtube_url))
        print("Success! Your audio file has been downloaded and converted.")

    except yt_dlp.utils.DownloadError as e:
        print(f"An error occurred while downloading: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Prompt the user to input the YouTube video link
    url = input("Enter the YouTube URL: ").strip()

    if url:
        download_youtube_audio(url)
    else:
        print("Invalid URL provided.")

    print(f"looking for url {url}")
    play_audio(url)
