import json
import re

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from collections import deque
from dataclasses import dataclass

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

socketio = SocketIO(app, cors_allowed_origins="*")


@dataclass()
class Song:
    """
    Class for holding a song object
    """

    link: str
    title: str
    user: str


class User:
    def __init__(self, name: str) -> None:
        self.name = name


class GBoxQueue:
    """
    Class for handleing the queue in GBox
    """

    def __init__(self) -> None:
        self.queue = deque()
        self.current_song = None

    def bump_up(self, item: Song) -> None:
        """
        For the Admin to bump up a specific song
        """
        pass

    def bump_down(self, item: Song) -> None:
        """
        For the Admin to bump down a specific song
        """
        pass

    def add_song(self, item: Song) -> None:
        """
        Add a song to the queue
        """
        pass

    def remove_song(self, item: Song) -> None:
        """
        Remove a song from the queue
        """
        pass

    def get_next_song(self) -> Song:
        """
        Pop the next song off and return it
        """
        pass


@app.route("/")
def index():
    return render_template("index.html")


# def background_counter():
#     count = 0
#
#     while True:
#         count += 1
#
#         socketio.emit(
#             "backend_update",
#             {"count": count, "message": f"Backend count is now {count}"},
#         )
#
#         socketio.sleep(1)


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("server_message", {"message": "Connected to Flask socket!"})
    global q
    q = GBoxQueue()


@socketio.on("client_message")
def handle_client_message(data):
    song_info = json.load(data)
    song = Song(song_info["link"], song_info["title"], song_info["user"])
    global q
    q.add_song(song)


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)


def validtae_youtube_url(url):
    pattern = r"^https?://(www\.)?(youtube\.con/watch\?v=[A-Za-z0-9_-]{11}(&.*)?|youtu\.be/[A-Za-z0-9_-]{11}(\?.*)?)$)"
    if re.match(pattern, url):
        return True
    return False


def extract_video_id(url):
    match = re.search(r"[?&]v-([A-Za-z0-9_-]{11})|youtu\.be/([A-Za-z0-9_-]{11})", url)
    return match.group(1) or match.group(2) if match else None
