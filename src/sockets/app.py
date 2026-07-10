import json
import re

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from collections import deque
from dataclasses import dataclass

from constants import yt_id_regex, yt_url_regex

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

    def __str__(self) -> str:
        return str([song for song in self.queue])

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
        self.queue.append(item)

    def remove_song(self, item: Song) -> None:
        """
        Remove a song from the queue
        """
        pass

    def get_next_song(self) -> Song:
        """
        Pop the next song off and return it
        """
        return Song("", "", "")


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

q = GBoxQueue()


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("server_message", {"message": "Connected to Flask socket!"})


@socketio.on("client_message")
def handle_client_message(data):
    print(data)
    print(type(data))
    try:
        validate_yt_url(data["url"])
    except:
        pass
    print("YAYYAYAYAYAYAYAYAY")

    # do the thing to download the song and then yeah yeah yeah

    q.add_song(Song(data["url"], "Last Carnival", "Fred"))
    print(q)


# if __name__ == "__main__":
#     socketio.run(app, host="127.0.0.1", port=5000, debug=True)


def validate_yt_url(url):
    if re.match(yt_url_regex, url):
        return True
    return False


def extract_video_id(url):
    match = re.search(yt_id_regex, url)
    return match.group(1) or match.group(2) if match else None


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
