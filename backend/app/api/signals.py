"""Signals API endpoints for pressure trends and weather flags."""
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import SignalsResponse, PressureTrend, SignalFlag
from app.services.weather_providers import fetch_from_providers
from app.services.signal_calculator import SignalCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["signals"])


@router.get("/signals", response_model=SignalsResponse)
async def get_signals(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    hours: int = Query(120, description="Forecast horizon in hours", ge=1, le=240),
    window: List[int] = Query([6, 12, 24], description="ΔP calculation windows in hours"),
    thresholds: Optional[str] = Query(
        None,
        description="Custom thresholds as JSON (optional)"
    )
):
    """
    Calculate pressure trends and detect weather signals.

    Args:
        lat: Latitude
        lon: Longitude
        hours: Forecast horizon
        window: Time windows for ΔP calculation (e.g., [6, 12, 24])
        thresholds: Optional JSON string with custom thresholds

    Returns:
        SignalsResponse with pressure trends and flags
    """
    try:
        # Fetch forecast data
        forecast_data = await fetch_from_providers(
            providers=["open-meteo"],  # Use primary provider
            lat=lat,
            lon=lon,
            hours=hours,
            include=["mslp", "wind", "cloud", "precip"]
        )

        if not forecast_data:
            raise HTTPException(
                status_code=503,
                detail="No forecast data available"
            )

        # Parse thresholds if provided
        custom_thresholds = None
        if thresholds:
            import json
            try:
                custom_thresholds = json.loads(thresholds)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON in thresholds parameter"
                )

        # Initialize calculator
        calculator = SignalCalculator(thresholds=custom_thresholds)

        # Calculate pressure deltas
        delta_result = calculator.calculate_pressure_deltas(forecast_data, windows=window)
        deltas = delta_result["deltas"]

        # Detect flags
        flags_data = calculator.detect_flags(forecast_data, deltas)

        # Get latest trend (most recent point)
        latest_delta = deltas[-1] if deltas else {}
        trend = PressureTrend(
            dP6_hpa=latest_delta.get("dP6_hpa"),
            dP12_hpa=latest_delta.get("dP12_hpa"),
            dP24_hpa=latest_delta.get("dP24_hpa")
        )

        # Convert flags
        flags = [SignalFlag(**flag) for flag in flags_data]

        logger.info(f"Signals: {len(flags)} flags detected for ({lat}, {lon})")

        return SignalsResponse(trend=trend, flags=flags)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
