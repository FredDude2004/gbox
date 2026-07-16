import os

from .player import VLCPlayer
from .queue import GBoxQueue


class Config:
    """Application configuration and shared runtime services."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    QUEUE = GBoxQueue()
    PLAYER = VLCPlayer(QUEUE)
