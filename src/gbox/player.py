import logging
import queue
import shutil
import subprocess
import threading
import time

from queue import Queue

from .constants import *
from .queue import GBoxQueue

logger = logging.getLogger(__name__)


class VLCPlayer:
    """Play audio files sequentially using one short-lived VLC process per track.

    Python owns the queue instead of VLC. This prevents VLC from replaying the
    previously selected track when playback has ended and a new track is added.
    """

    def __init__(self, queue: GBoxQueue) -> None:
        self._vlc_binary = self.find_vlc_binary()

        self.command_queue: Queue[tuple[str, str | None]] = Queue()
        self.process: subprocess.Popen[str] | None = None

        self.gbox_queue: GBoxQueue = queue

        self.worker_thread = None
        self.current_audio_process = None
        self.lock = threading.Lock()
        self.shutdown = threading.Event()

    @staticmethod
    def find_vlc_binary():
        for candidate in ("cvlc", "vlc"):
            path = shutil.which(candidate)
            if path:
                return candidate
        raise RuntimeError(
            "Could not find 'cvlc' or 'vlc' on PATH. Please install VLC."
        )

    def start(self) -> None:
        if self.worker_thread is not None:
            return
        self.shutdown.clear()
        self.worker_thread = threading.Thread(
            target=self.worker, name="VLCPlayerWorker", daemon=True
        )
        self.worker_thread.start()

    def worker(self) -> None:
        while True:
            # handle any pending control commands first
            command_result = self.check_if_closed()
            if command_result == "closed":
                break

            # if nothing is playing, try to pull the next file and start it
            with self.lock:
                has_current = self.current_audio_process is not None

            if not has_current:
                try:
                    song = self.gbox_queue.get_next_song()
                    audio_file_path = song.file_path
                except Exception as e:
                    logger.debug(e)
                    continue
                self.start_audio(audio_file_path)
                continue

            # something is playing, check whether it has finished on its own
            with self.lock:
                proc = self.current_audio_process
            if proc is not None and proc.poll() is not None:
                self.cleanup_current_process()

            time.sleep(POLL_INTERVAL)

        # final cleanup on shutdown
        self.cleanup_current_process(force=True)

    def check_if_closed(self):
        while True:
            try:
                cmd, _ = self.command_queue.get_nowait()
            except queue.Empty:
                return None

            if cmd == "pause":
                logger.info("[VLCPlayer] Sending pause/play")
                self.send_pause()
            elif cmd == "next":
                logger.info("[VLCPlayer] Sending skip")
                self.cleanup_current_process(force=True)
            elif cmd == "stop":
                logger.info("[VLCPlayer] Sending stop")
                self.cleanup_current_process(force=True)
            elif cmd == "close":
                self.gbox_queue.clear_queue()
                self.cleanup_current_process(force=True)
                self.shutdown.set()
                return "closed"

    def start_audio(self, path) -> None:
        args = [
            self._vlc_binary,
            "--no-video",
            "--play-and-exit",
            "--intf",
            "rc",
            path,
        ]

        try:
            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
        except OSError as exc:
            print(f"[AudioQueuePlayer] Failed to start VLC for {path}: {exc}")
            return

        with self.lock:
            self.current_audio_process = proc
        logger.debug(f"[VLCPlayer] Now playing: {path}")

    def send_pause(self) -> None:
        with self.lock:
            proc = self.current_audio_process
        if proc is None or proc.poll() is not None:
            return
        if proc is None or proc.poll() is not None or proc.stdin is None:
            return

        try:
            proc.stdin.write("pause\n")
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def cleanup_current_process(self, force=False):
        with self.lock:
            proc = self.current_audio_process
            self.current_audio_process = None

        if proc is None:
            return

        if force and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        else:
            proc.wait()

        try:
            if proc.stdin:
                proc.stdin.close()
        except OSError:
            pass

    def pause(self):
        """Toggle pause/resume on the currently playing track."""

        self.command_queue.put(("pause", None))

    def next(self):
        """Stop the current track and immediately advance to the next one."""

        self.command_queue.put(("next", None))

    def stop(self):
        """Stop the current track without clearing the remaining queue."""

        self.command_queue.put(("stop", None))

    def close(self):
        """
        Clear the pending queue, stop the active track, and shut down the
        worker thread cleanly. Blocks until the worker has exited.
        """

        self.command_queue.put(("close", None))
        if self._worker_thread is not None:
            self._worker_thread.join()
            self._worker_thread = None
