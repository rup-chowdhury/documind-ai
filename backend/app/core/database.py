from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/documind"


class Base(DeclarativeBase):
    """Base class inherited by every SQLAlchemy model."""


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session for one FastAPI request."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()