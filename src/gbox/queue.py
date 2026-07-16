import json
import logging
import threading

from .model import Song

logger = logging.getLogger(__name__)


class GBoxQueue:
    """
    Class for handleing the queue in GBox
    """

    def __init__(self) -> None:
        self.queue: list[Song] = []
        self.current_song = None
        self.lock = threading.Lock()

    def __str__(self) -> str:
        return json.dumps(
            [{"title": entry.title, "user": entry.username} for entry in self.queue]
        )

    def clear_queue(self) -> None:
        self.queue = []

    def is_empty(self) -> bool:
        return self.queue == []

    def to_view_list(self) -> list:
        return [{"title": entry.title, "user": entry.username} for entry in self.queue]

    def bump_up(self, item: Song) -> None:
        """
        For the Admin to bump up a specific song
        """
        with self.lock:
            try:
                idx = self.queue.index(item)
            except ValueError:
                logger.info("[GBoxQueue] Song not in queue: %s", item)
                return

            if idx == 0:
                logger.info("[GBoxQueue] Song is already first in the queue")
                return

            self.queue[idx - 1], self.queue[idx] = (
                self.queue[idx],
                self.queue[idx - 1],
            )

    def bump_down(self, item) -> None:
        """
        For the Admin to bump down a specific song
        """
        if not isinstance(item, Song):
            logger.error(
                "GBoxQueue only accepts Song objects, got %s",
                type(item).__name__,
            )
            return

        with self.lock:
            try:
                idx = self.queue.index(item)
                assert idx < len(
                    self.queue
                ), "Error: Cannot move the song further up the queue"
                tmp = self.queue[idx]
                self.queue[idx] = self.queue[idx + 1]
                self.queue[idx + 1] = tmp
            except ValueError:
                # the song is not in the queue
                pass
            except AssertionError:
                # the song is already at the top of the queue
                pass
            finally:
                pass

    def add_song(self, item) -> None:
        """
        Add a song to the queue
        """
        if not isinstance(item, Song):
            logger.error(
                "GBoxQueue only accepts Song objects, got %s",
                type(item).__name__,
            )
            return

        with self.lock:
            self.queue.append(item)

    def remove_song(self, item) -> None:
        """
        Remove a song from the queue
        """
        if not isinstance(item, Song):
            logger.error(
                "GBoxQueue only accepts Song objects, got %s",
                type(item).__name__,
            )
            return

        with self.lock:
            if item in self.queue:
                self.queue.remove(item)

    def get_next_song(self) -> Song:
        """
        Pop the next song off and return it
        """

        with self.lock:
            if self.queue:
                self.current_song = self.queue.pop(0)
                return self.current_song

            raise Exception("Error: GBoxQueue is empty no next song")
