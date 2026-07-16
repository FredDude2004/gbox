from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "gbox.db"
AUDIO_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "audios"

ADMIN_PASSWORD = "password"
SECRET_KEY = "super_secret_key"

PORT = 42069
