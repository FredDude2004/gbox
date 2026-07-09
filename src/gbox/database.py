from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

from .constants import DATABASE_PATH

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False}
)


def init_db() -> None:
    """Initializes the database and creates all tables."""
    import model

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yields a database connection session."""
    with Session(engine) as session:
        yield session
