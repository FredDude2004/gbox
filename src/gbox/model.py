from typing import List
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field
from flask_login import UserMixin


class Song(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    url: str
    video_id: str
    title: str | None
    uploader: str | None
    duration: int | None
    view_count: int | None
    file_path: str


class User(UserMixin, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    songs: List[str] = Field(default_factory=list, sa_type=JSON)
