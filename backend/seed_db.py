"""Seed database with initial waterbodies."""
import json
import logging
from pathlib import Path

from sqlmodel import Session, select

from app.core.database import create_db_and_tables, engine
from app.models.database import WaterbodyDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_waterbodies():
    """Load waterbodies from seed_waterbodies.json."""
    seed_file = Path(__file__).parent / "seed_waterbodies.json"

    if not seed_file.exists():
        logger.error(f"Seed file not found: {seed_file}")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        waterbodies_data = json.load(f)

    with Session(engine) as session:
        # Check if waterbodies already exist
        existing = session.exec(select(WaterbodyDB)).all()
        if existing:
            logger.info(f"Database already contains {len(existing)} waterbodies, skipping seed")
            return

        # Insert waterbodies
        for wb_data in waterbodies_data:
            waterbody = WaterbodyDB(**wb_data)
            session.add(waterbody)

        session.commit()
        logger.info(f"Seeded {len(waterbodies_data)} waterbodies")


if __name__ == "__main__":
    logger.info("Creating database tables...")
    create_db_and_tables()

    logger.info("Seeding waterbodies...")
    seed_waterbodies()

    logger.info("Database seeding complete!")
