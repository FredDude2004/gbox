from collections import deque


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
