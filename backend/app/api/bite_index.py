"""Bite index API endpoints."""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import BiteIndexResponse, BiteIndexMeta, BiteIndexHourly
from app.services.weather_providers import fetch_from_providers
from app.services.signal_calculator import SignalCalculator
from app.services.bite_index import BiteIndexCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["bite-index"])


@router.get("/bite-index", response_model=BiteIndexResponse)
async def get_bite_index(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    hours: int = Query(120, description="Forecast horizon in hours", ge=1, le=240),
    species: List[str] = Query(
        ["pike", "perch"],
        description="Target species (pike, walleye, perch, bream)"
    )
):
    """
    Calculate bite index for ice fishing.

    Args:
        lat: Latitude
        lon: Longitude
        hours: Forecast horizon
        species: Target species for index calculation

    Returns:
        BiteIndexResponse with hourly scores, explanations, and confidence
    """
    try:
        # Fetch forecast data
        forecast_data = await fetch_from_providers(
            providers=["open-meteo"],
            lat=lat,
            lon=lon,
            hours=hours,
            include=["mslp", "t2m", "wind", "gust", "cloud", "precip", "snowfall", "snow_depth"]
        )

        if not forecast_data:
            raise HTTPException(
                status_code=503,
                detail="No forecast data available"
            )

        # Calculate signals
        signal_calc = SignalCalculator()
        delta_result = signal_calc.calculate_pressure_deltas(forecast_data, windows=[6, 12, 24])
        deltas = delta_result["deltas"]
        flags = signal_calc.detect_flags(forecast_data, deltas)

        # Calculate bite index
        bite_calc = BiteIndexCalculator()
        result = bite_calc.calculate_index(
            forecast_data=forecast_data,
            deltas=deltas,
            flags=flags,
            species=species
        )

        # Build response
        meta = BiteIndexMeta(species=species)
        hourly = [BiteIndexHourly(**point) for point in result["hourly"]]
        confidence = result["confidence"]

        logger.info(f"Bite index: {len(hourly)} points for ({lat}, {lon}), species={species}, confidence={confidence}")

        return BiteIndexResponse(meta=meta, hourly=hourly, confidence=confidence)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating bite index: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
