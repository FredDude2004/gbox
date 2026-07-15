from typing import List

from .model import Song


class GBoxQueue:
    """
    Class for handleing the queue in GBox
    """

    def __init__(self) -> None:
        self.queue: List[Song] = []
        self.current_song = None

    def bump_up(self, item: Song) -> None:
        """
        For the Admin to bump up a specific song
        """
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
        self.queue.append(item)

    def remove_song(self, item: Song) -> None:
        """
        Remove a song from the queue
        """
        if item in self.queue:
            self.queue.remove(item)

    def get_next_song(self) -> Song:
        """
        Pop the next song off and return it
        """
        if self.queue:
            return self.queue.pop()
