import json
import threading

from .model import Song


class GBoxQueue:
    """
    Class for handleing the queue in GBox
    """

    def __init__(self) -> None:
        self.queue: list[Song] = []
        self.current_song = None
        self._lock = threading.Lock()

    def __str__(self) -> str:
        return json.dumps(
            [{"title": entry.title, "user": entry.username} for entry in self.queue]
        )

    def clear(self) -> None:
        self.queue = []

    def to_json(self) -> list:
        return [{"title": entry.title, "user": entry.username} for entry in self.queue]

    def bump_up(self, item: Song) -> None:
        """
        For the Admin to bump up a specific song
        """
        with self._lock:
            try:
                idx = self.queue.index(item)
                assert idx >= 0, "Error: Cannot move the song further up the queue"
                tmp = self.queue[idx]
                self.queue[idx] = self.queue[idx - 1]
                self.queue[idx - 1] = tmp
            except ValueError:
                # the song is not in the queue
                pass
            except AssertionError:
                # the song is already at the top of the queue
                pass
            finally:
                pass

    def bump_down(self, item: Song) -> None:
        """
        For the Admin to bump down a specific song
        """
        with self._lock:
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

    def add_song(self, item: Song) -> None:
        """
        Add a song to the queue
        """
        assert isinstance(item, Song), "Error: Can only append Song's to the queue"
        with self._lock:
            self.queue.append(item)

    def remove_song(self, item: Song) -> None:
        """
        Remove a song from the queue
        """
        if item in self.queue:
            self.queue.remove(item)

    def get_next_song(self) -> Song | None:
        """
        Pop the next song off and return it
        """

        with self._lock:
            if self.queue:
                self.current_song = self.queue.pop()
                return self.current_song
