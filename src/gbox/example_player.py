"""
audio_queue_player.py

A simple, lightweight FIFO audio queue player built on top of VLC's
command-line interface (cvlc). A background worker thread owns the queue,
starts/stops VLC subprocesses, and advances to the next track automatically
when the current one finishes.

Requires the VLC command-line binary ('cvlc' or 'vlc') to be installed and
on PATH.
"""

import os
import queue
import shutil
import subprocess
import sys
import threading
import time


class AudioQueuePlayer:
    """FIFO audio queue player that drives VLC subprocesses."""

    # Poll interval (seconds) the worker uses to check for finished
    # processes / new commands. Small enough to feel responsive,
    # large enough to avoid busy-waiting.
    _POLL_INTERVAL = 0.2

    def __init__(self, vlc_binary=None):
        self._vlc_binary = vlc_binary or self._find_vlc_binary()

        self._file_queue = queue.Queue()  # pending track paths (FIFO)
        self._cmd_queue = queue.Queue()  # control commands for worker

        self._worker_thread = None
        self._shutdown = threading.Event()

        self._current_process = None
        self._state_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Setup helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_vlc_binary():
        for candidate in ("cvlc", "vlc"):
            path = shutil.which(candidate)
            if path:
                return candidate
        raise RuntimeError(
            "Could not find 'cvlc' or 'vlc' on PATH. Please install VLC."
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def start(self):
        """Start the background worker thread."""
        if self._worker_thread is not None:
            return
        self._shutdown.clear()
        self._worker_thread = threading.Thread(
            target=self._worker_loop, name="AudioQueuePlayerWorker", daemon=True
        )
        self._worker_thread.start()

    def add(self, audio_path):
        """
        Validate and enqueue an audio file.

        Returns True if the file was queued, False if it failed validation.
        Playback starts automatically if the player is currently idle.
        """
        if not audio_path:
            return False

        if not os.path.isfile(audio_path):
            print(f"[AudioQueuePlayer] Invalid file path: {audio_path}")
            return False

        self._file_queue.put(audio_path)
        return True

    def pause(self):
        """Toggle pause/resume on the currently playing track."""
        self._cmd_queue.put(("pause", None))

    def next(self):
        """Stop the current track and immediately advance to the next one."""
        self._cmd_queue.put(("next", None))

    def stop(self):
        """Stop the current track without clearing the remaining queue."""
        self._cmd_queue.put(("stop", None))

    def close(self):
        """
        Clear the pending queue, stop the active track, and shut down the
        worker thread cleanly. Blocks until the worker has exited.
        """
        self._cmd_queue.put(("close", None))
        if self._worker_thread is not None:
            self._worker_thread.join()
            self._worker_thread = None

    # ------------------------------------------------------------------ #
    # Worker thread internals
    # ------------------------------------------------------------------ #

    def _worker_loop(self):
        while True:
            # 1. Handle any pending control commands first.
            command_result = self._drain_commands()
            if command_result == "closed":
                break

            # 2. If nothing is playing, try to pull the next file and start it.
            with self._state_lock:
                has_current = self._current_process is not None

            if not has_current:
                try:
                    next_path = self._file_queue.get(timeout=self._POLL_INTERVAL)
                except queue.Empty:
                    continue
                self._start_track(next_path)
                continue

            # 3. Something is playing: check whether it has finished on its own.
            with self._state_lock:
                proc = self._current_process
            if proc is not None and proc.poll() is not None:
                # Track finished naturally; clean up and loop back to fetch next.
                self._cleanup_current_process()

            time.sleep(self._POLL_INTERVAL)

        # Final cleanup on shutdown.
        self._cleanup_current_process(force=True)

    def _drain_commands(self):
        """Process all queued commands without blocking. Returns 'closed' if
        a close command was handled."""
        while True:
            try:
                cmd, _ = self._cmd_queue.get_nowait()
            except queue.Empty:
                return None

            if cmd == "pause":
                self._send_pause()
            elif cmd == "next":
                self._cleanup_current_process(force=True)
            elif cmd == "stop":
                self._cleanup_current_process(force=True)
            elif cmd == "close":
                self._clear_pending_queue()
                self._cleanup_current_process(force=True)
                self._shutdown.set()
                return "closed"

    def _start_track(self, path):
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

        with self._state_lock:
            self._current_process = proc
        print(f"[AudioQueuePlayer] Now playing: {path}")

    def _send_pause(self):
        with self._state_lock:
            proc = self._current_process
        if proc is None or proc.poll() is not None:
            return
        if proc is None or proc.poll() is not None or proc.stdin is None:
            return

        try:
            proc.stdin.write("pause\n")
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass

    def _cleanup_current_process(self, force=False):
        with self._state_lock:
            proc = self._current_process
            self._current_process = None

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

    def _clear_pending_queue(self):
        while True:
            try:
                self._file_queue.get_nowait()
            except queue.Empty:
                break


# ---------------------------------------------------------------------- #
# Command-line interface
# ---------------------------------------------------------------------- #


def main():
    try:
        player = AudioQueuePlayer()
    except RuntimeError as exc:
        print(str(exc))
        sys.exit(1)

    player.start()
    print("Audio queue player started. Enter audio file paths to queue them.")
    print("Type 'quit', 'exit', or 'q' to stop. Ctrl+C also exits.")

    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print("\nEnd of input, shutting down.")
                break

            if not line:
                continue

            if line.lower() in ("quit", "exit", "q"):
                print("Shutting down.")
                break

            if player.add(line):
                print(f"Queued: {line}")
    except KeyboardInterrupt:
        print("\nInterrupted, shutting down.")
    finally:
        player.close()
        print("Player closed.")


if __name__ == "__main__":
    main()


# Can you write a simple and lightweight Python-based audio queue player that uses VLC to play local audio files sequentially.
# The program maintains a first-in, first-out queue of audio file paths. Audio files can be added to the queue at any time, including while another file is already playing or while the player is idle. When playback is idle, adding a valid audio file automatically begins playback.
# The Python application runs a dedicated background worker thread that manages the queue, receives playback commands, and controls VLC. Each audio file is played in its own VLC subprocess. When the current file finishes, the VLC subprocess exits and the worker automatically starts the next queued file.
#
# The player must:

# - Be written in Python.
# - Use VLC's command-line interface to play local audio files.
# - Accept audio file paths while the program is running.
# - Validate that each provided path refers to an existing file.
# - Store valid files in a first-in, first-out playback queue.
# - Automatically play the first queued file when the player is idle.
# - Automatically advance to the next queued file when the current file finishes.
# - Continue running indefinitely when the queue is empty.
# - Allow new files to be queued while another file is playing.
# - Avoid replaying previously completed files when playback resumes from an idle state.
# - Run playback management in a background worker thread so the main thread remains available for user input.
# - Run each track in a separate VLC subprocess with video disabled.
# - Shut down each VLC subprocess after its track finishes.
# - Shut down the background worker only when the main program exits.

# - The player exposes the following operations:

# start() starts the background worker thread.
# add(audio_path) validates and adds an audio file to the queue. If the player is idle, playback begins automatically.
# pause() sends VLC's pause command, which toggles between paused and playing states.
# next() stops the current track and immediately starts the next queued track.
# stop() stops the current track without clearing the remaining queue.
# close() clears the pending queue, stops the active VLC subprocess, and waits for the worker thread to exit cleanly.

# The main program provides a command-line interface where the user can continuously enter paths to audio files. Empty input is ignored. Entering quit, exit, or q, pressing Ctrl+C, or reaching the end of input causes the player to shut down gracefully.
