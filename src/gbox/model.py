import os

from enum import Enum
from flask_login import UserMixin
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field
from typing import List

from .constants import *
from .player import Player
from .queue import GBoxQueue


class Song(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    video_id: str
    title: str | None
    uploader: str | None
    duration: int | None
    view_count: int | None
    file_path: str

    username: str | None


class User(UserMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    songs: List[str] = Field(default_factory=list, sa_type=JSON)


class Config:
    """Application configuration with secure defaults"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24)
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    QUEUE = GBoxQueue()
    PLAYER = Player(QUEUE)


class PlayerState(Enum):
    STOPPED = 0
    IDLE = 1
    PLAYING = 2
