from pathlib import Path

# downloader.py
DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "gbox.db"
AUDIO_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "audios"

# model.py
ADMIN_PASSWORD = "password"
SECRET_KEY = "super_secret_key"

# app.py
PORT = 42069

# player.py
POLL_INTERVAL = 0.2
