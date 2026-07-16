import logging
import time

from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event  # Import the event module

from .constants import DATABASE_PATH

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False}
)

logger = logging.getLogger(__name__)


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    connection_record.info["start_time"] = time.perf_counter()


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    start_time = connection_record.info.get("start_time")
    if start_time:
        duration = time.perf_counter() - start_time
        logger.debug(f"Database connection life cycle lasted: {duration:.6f}s")


def init_db() -> None:
    """Initializes the database and creates all tables."""

    import model

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yields a database connection session."""

    with Session(engine) as session:
        yield session
