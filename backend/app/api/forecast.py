"""Forecast API endpoints."""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import ForecastResponse, ForecastMeta, HourlyForecast
from app.services.weather_providers import fetch_from_providers

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["forecast"])


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    hours: int = Query(120, description="Forecast horizon in hours", ge=1, le=240),
    provider: List[str] = Query(
        ["open-meteo"],
        description="Weather providers to use"
    ),
    include: List[str] = Query(
        ["mslp", "t2m", "wind", "gust", "cloud", "precip", "snowfall", "snow_depth"],
        description="Fields to include in response"
    )
):
    """
    Get weather forecast from configured providers.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        hours: Forecast horizon in hours (default: 120)
        provider: List of providers (open-meteo, metno, openweather)
        include: List of fields to include

    Returns:
        ForecastResponse with hourly data from requested providers
    """
    try:
        # Fetch from providers
        hourly_data = await fetch_from_providers(
            providers=provider,
            lat=lat,
            lon=lon,
            hours=hours,
            include=include
        )

        if not hourly_data:
            raise HTTPException(
                status_code=503,
                detail="No forecast data available from any provider"
            )

        # Build response
        meta = ForecastMeta(
            lat=lat,
            lon=lon,
            timezone="Europe/Moscow",
            providers=list(set(p["provider"] for p in hourly_data))
        )

        hourly = [HourlyForecast(**point) for point in hourly_data]

        logger.info(f"Forecast: {len(hourly)} points for ({lat}, {lon}) from {meta.providers}")

        return ForecastResponse(meta=meta, hourly=hourly)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
