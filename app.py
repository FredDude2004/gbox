import sqlite3
import shortuuid


from flask import Flask
from collections import deque
from dataclasses import dataclass

app = Flask(__name__)


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
        self.id = shortuuid.uuid()[:4]


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
def hello_world():
    return "<p>Nutz Deez</p>"
