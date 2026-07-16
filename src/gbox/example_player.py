from collections import deque
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import subprocess


class VLCPlayer:
    """Play audio files sequentially using one short-lived VLC process per track.

    Python owns the queue instead of VLC. This prevents VLC from replaying the
    previously selected track when playback has ended and a new track is added.
    """

    def __init__(self) -> None:
        self.commands: Queue[tuple[str, str | None]] = Queue()
        self.process: subprocess.Popen[str] | None = None
        self.worker = Thread(target=self._run, daemon=True)

        # These fields are only accessed by the worker thread.
        self._pending: deque[Path] = deque()
        self._current: Path | None = None

    def start(self) -> None:
        self.worker.start()

    def add(self, audio_path: str) -> None:
        self.commands.put(("add", audio_path))

    def pause(self) -> None:
        self.commands.put(("pause", None))

    def next(self) -> None:
        self.commands.put(("next", None))

    def stop(self) -> None:
        self.commands.put(("stop", None))

    def close(self) -> None:
        self.commands.put(("quit", None))
        self.worker.join()

    def _send(self, command: str) -> None:
        process = self.process

        if process is not None and process.poll() is None and process.stdin is not None:
            try:
                process.stdin.write(command + "\n")
                process.stdin.flush()
            except (BrokenPipeError, OSError):
                # VLC may have exited naturally between poll() and write().
                pass

    def _start_next(self) -> None:
        """Start the next queued track when no track is currently running."""
        if self.process is not None or not self._pending:
            return

        path = self._pending.popleft()

        try:
            self.process = subprocess.Popen(
                [
                    "cvlc",
                    "--intf",
                    "rc",
                    "--rc-fake-tty",
                    "--play-and-exit",
                    "--no-video",
                    path.as_uri(),
                ],
                stdin=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            print("Could not find cvlc. Make sure VLC is installed.")
            self._pending.clear()
            return

        self._current = path
        print(f"Playing: {path.name}")

    def _reap_finished_track(self) -> bool:
        """Clean up a naturally finished VLC process.

        Returns True when a track finished, allowing the worker to immediately
        start the next queued track.
        """
        process = self.process

        if process is None or process.poll() is None:
            return False

        process.wait()
        self.process = None
        self._current = None
        return True

    def _end_current_track(self) -> None:
        """Stop the active VLC process and fully reap it."""
        process = self.process

        if process is None:
            return

        if process.poll() is None:
            self._send("quit")

            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.terminate()

                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        else:
            process.wait()

        self.process = None
        self._current = None

    def _run(self) -> None:
        while True:
            # A process exits when its track ends because of --play-and-exit.
            # Start the next Python-queued track rather than asking VLC to
            # resume its old internal playlist selection.
            if self._reap_finished_track():
                self._start_next()

            try:
                command, argument = self.commands.get(timeout=0.1)
            except Empty:
                continue

            if command == "add" and argument is not None:
                path = Path(argument).expanduser().resolve()

                if not path.is_file():
                    print(f"File does not exist: {path}")
                    continue

                self._pending.append(path)
                print(f"Queued: {path.name}")

                # If playback is idle, this starts exactly the newly queued
                # track (or the oldest pending track), never a completed one.
                if self.process is None:
                    self._start_next()

            elif command == "pause":
                self._send("pause")

            elif command == "next":
                self._end_current_track()
                self._start_next()

            elif command == "stop":
                self._end_current_track()

            elif command == "quit":
                self._pending.clear()
                self._end_current_track()
                break


def main() -> None:
    player = VLCPlayer()
    player.start()

    print("=" * 50)
    print("Simple VLC Queue Player")
    print("=" * 50)
    print("Enter the path to an audio file to add it to the queue.")
    print("Type 'quit' to exit.")
    print()

    while True:
        try:
            path = input("Audio file> ").strip()

            if not path:
                continue

            if path.lower() in {"quit", "exit", "q"}:
                break

            player.add(path)

        except KeyboardInterrupt:
            print()
            break
        except EOFError:
            print()
            break

    print("Closing player...")
    player.close()


if __name__ == "__main__":
    main()
