"""Waterbodies API endpoints (CRUD)."""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.database import WaterbodyDB
from app.models.schemas import Waterbody, WaterbodyCreate, WaterbodyUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["waterbodies"])


@router.get("/waterbodies", response_model=List[Waterbody])
async def list_waterbodies(
    region: str = None,
    type: str = None,
    session: Session = Depends(get_session)
):
    """
    List all waterbodies with optional filtering.

    Args:
        region: Filter by region (optional)
        type: Filter by type (reservoir, lake, river) (optional)
        session: Database session

    Returns:
        List of waterbodies
    """
    try:
        query = select(WaterbodyDB)

        if region:
            query = query.where(WaterbodyDB.region == region)
        if type:
            query = query.where(WaterbodyDB.type == type)

        waterbodies = session.exec(query).all()

        logger.info(f"Listed {len(waterbodies)} waterbodies")
        return waterbodies

    except Exception as e:
        logger.error(f"Error listing waterbodies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/waterbodies/{waterbody_id}", response_model=Waterbody)
async def get_waterbody(
    waterbody_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific waterbody by ID."""
    waterbody = session.get(WaterbodyDB, waterbody_id)

    if not waterbody:
        raise HTTPException(status_code=404, detail="Waterbody not found")

    return waterbody


@router.post("/waterbodies", response_model=Waterbody, status_code=201)
async def create_waterbody(
    waterbody: WaterbodyCreate,
    session: Session = Depends(get_session)
):
    """Create a new waterbody."""
    try:
        db_waterbody = WaterbodyDB(**waterbody.model_dump())
        session.add(db_waterbody)
        session.commit()
        session.refresh(db_waterbody)

        logger.info(f"Created waterbody: {db_waterbody.name}")
        return db_waterbody

    except Exception as e:
        session.rollback()
        logger.error(f"Error creating waterbody: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/waterbodies/{waterbody_id}", response_model=Waterbody)
async def update_waterbody(
    waterbody_id: int,
    waterbody: WaterbodyUpdate,
    session: Session = Depends(get_session)
):
    """Update a waterbody."""
    db_waterbody = session.get(WaterbodyDB, waterbody_id)

    if not db_waterbody:
        raise HTTPException(status_code=404, detail="Waterbody not found")

    try:
        # Update fields
        update_data = waterbody.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_waterbody, key, value)

        session.add(db_waterbody)
        session.commit()
        session.refresh(db_waterbody)

        logger.info(f"Updated waterbody: {db_waterbody.name}")
        return db_waterbody

    except Exception as e:
        session.rollback()
        logger.error(f"Error updating waterbody: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/waterbodies/{waterbody_id}", status_code=204)
async def delete_waterbody(
    waterbody_id: int,
    session: Session = Depends(get_session)
):
    """Delete a waterbody."""
    waterbody = session.get(WaterbodyDB, waterbody_id)

    if not waterbody:
        raise HTTPException(status_code=404, detail="Waterbody not found")

    try:
        session.delete(waterbody)
        session.commit()

        logger.info(f"Deleted waterbody: {waterbody.name}")
        return None

    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting waterbody: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
