"""Database connection and session management."""
import logging
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Ensure data directory exists
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
