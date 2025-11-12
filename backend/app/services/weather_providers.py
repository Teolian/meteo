"""Weather data providers integration."""
import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from app.core.cache import memory_cache
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenMeteoProvider:
    """Open-Meteo weather provider."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    @memory_cache(ttl_minutes=60)
    async def fetch_forecast(
        lat: float,
        lon: float,
        hours: int = 120,
        include: Optional[List[str]] = None
    ) -> Dict:
        """Fetch forecast from Open-Meteo."""
        if include is None:
            include = ["mslp", "t2m", "wind", "cloud", "precip", "snowfall", "snow_depth"]

        # Map our field names to Open-Meteo parameter names
        param_map = {
            "mslp": "pressure_msl",
            "t2m": "temperature_2m",
            "wind": "wind_speed_10m,wind_direction_10m",
            "gust": "wind_gusts_10m",
            "cloud": "cloud_cover",
            "precip": "precipitation",
            "snowfall": "snowfall",
            "snow_depth": "snow_depth",
            "visibility": "visibility"
        }

        hourly_params = []
        for field in include:
            if field in param_map:
                hourly_params.extend(param_map[field].split(","))

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_params),
            "timezone": settings.tz,
            "forecast_days": min(16, (hours // 24) + 1)
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                logger.info(f"Open-Meteo: fetched {len(data.get('hourly', {}).get('time', []))} hours for ({lat}, {lon})")
                return self._normalize_response(data, hours)

        except httpx.HTTPError as e:
            logger.error(f"Open-Meteo HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Open-Meteo error: {e}")
            raise

    @staticmethod
    def _normalize_response(data: Dict, hours: int) -> List[Dict]:
        """Normalize Open-Meteo response to our schema."""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])[:hours]

        result = []
        for i, time_str in enumerate(times):
            point = {
                "time": time_str,
                "mslp_hpa": hourly.get("pressure_msl", [])[i] if i < len(hourly.get("pressure_msl", [])) else None,
                "t2m_c": hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else None,
                "wind10_mps": hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else None,
                "wind_dir_deg": hourly.get("wind_direction_10m", [])[i] if i < len(hourly.get("wind_direction_10m", [])) else None,
                "gust_mps": hourly.get("wind_gusts_10m", [])[i] if i < len(hourly.get("wind_gusts_10m", [])) else None,
                "cloud_pct": hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else None,
                "precip_mm": hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else None,
                "snowfall_mm": hourly.get("snowfall", [])[i] if i < len(hourly.get("snowfall", [])) else None,
                "snow_depth_cm": hourly.get("snow_depth", [])[i] if i < len(hourly.get("snow_depth", [])) else None,
                "visibility_km": hourly.get("visibility", [])[i] / 1000 if i < len(hourly.get("visibility", [])) and hourly.get("visibility", [])[i] else None,
                "provider": "open-meteo"
            }
            result.append(point)

        return result


class METNorwayProvider:
    """MET Norway Locationforecast provider."""

    BASE_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

    @staticmethod
    @memory_cache(ttl_minutes=60)
    async def fetch_forecast(
        lat: float,
        lon: float,
        hours: int = 120,
        include: Optional[List[str]] = None
    ) -> Dict:
        """Fetch forecast from MET Norway."""
        headers = {
            "User-Agent": settings.metno_user_agent
        }

        params = {
            "lat": lat,
            "lon": lon
        }

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                logger.info(f"MET Norway: fetched forecast for ({lat}, {lon})")
                return self._normalize_response(data, hours)

        except httpx.HTTPError as e:
            logger.error(f"MET Norway HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"MET Norway error: {e}")
            raise

    @staticmethod
    def _normalize_response(data: Dict, hours: int) -> List[Dict]:
        """Normalize MET Norway response to our schema."""
        timeseries = data.get("properties", {}).get("timeseries", [])[:hours]

        result = []
        for entry in timeseries:
            time_str = entry.get("time")
            instant = entry.get("data", {}).get("instant", {}).get("details", {})

            point = {
                "time": time_str,
                "mslp_hpa": instant.get("air_pressure_at_sea_level"),
                "surface_pressure_hpa": instant.get("air_pressure_at_sea_level"),  # MET Norway uses same field
                "t2m_c": instant.get("air_temperature"),
                "wind10_mps": instant.get("wind_speed"),
                "wind_dir_deg": int(instant.get("wind_from_direction")) if instant.get("wind_from_direction") else None,
                "gust_mps": instant.get("wind_speed_of_gust"),
                "cloud_pct": int(instant.get("cloud_area_fraction")) if instant.get("cloud_area_fraction") else None,
                "visibility_km": instant.get("fog_area_fraction"),  # Approximation
                "provider": "metno"
            }

            # Try to get precipitation from next_1_hours
            next_1h = entry.get("data", {}).get("next_1_hours", {}).get("details", {})
            if next_1h:
                point["precip_mm"] = next_1h.get("precipitation_amount")

            result.append(point)

        return result


class OpenWeatherProvider:
    """OpenWeather One Call 3.0 provider (optional/fallback)."""

    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

    @staticmethod
    @memory_cache(ttl_minutes=60)
    async def fetch_forecast(
        lat: float,
        lon: float,
        hours: int = 120,
        include: Optional[List[str]] = None
    ) -> Dict:
        """Fetch forecast from OpenWeather."""
        if not settings.openweather_key:
            logger.warning("OpenWeather API key not configured")
            return []

        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.openweather_key,
            "units": "metric",
            "exclude": "minutely,daily,alerts"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                logger.info(f"OpenWeather: fetched forecast for ({lat}, {lon})")
                return self._normalize_response(data, hours)

        except httpx.HTTPError as e:
            logger.error(f"OpenWeather HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenWeather error: {e}")
            raise

    @staticmethod
    def _normalize_response(data: Dict, hours: int) -> List[Dict]:
        """Normalize OpenWeather response to our schema."""
        hourly_data = data.get("hourly", [])[:hours]

        result = []
        for entry in hourly_data:
            # Convert timestamp to ISO format
            dt = datetime.fromtimestamp(entry.get("dt"))
            time_str = dt.isoformat()

            point = {
                "time": time_str,
                "mslp_hpa": entry.get("pressure"),
                "t2m_c": entry.get("temp"),
                "wind10_mps": entry.get("wind_speed"),
                "wind_dir_deg": entry.get("wind_deg"),
                "gust_mps": entry.get("wind_gust"),
                "cloud_pct": entry.get("clouds"),
                "visibility_km": entry.get("visibility", 0) / 1000,
                "provider": "openweather"
            }

            # Precipitation
            if "rain" in entry:
                point["precip_mm"] = entry["rain"].get("1h", 0)
            if "snow" in entry:
                point["snowfall_mm"] = entry["snow"].get("1h", 0)

            result.append(point)

        return result


# Provider registry
PROVIDERS = {
    "open-meteo": OpenMeteoProvider(),
    "metno": METNorwayProvider(),
    "openweather": OpenWeatherProvider()
}


async def fetch_from_providers(
    providers: List[str],
    lat: float,
    lon: float,
    hours: int = 120,
    include: Optional[List[str]] = None
) -> List[Dict]:
    """Fetch forecast from multiple providers."""
    results = []

    for provider_name in providers:
        if provider_name not in PROVIDERS:
            logger.warning(f"Unknown provider: {provider_name}")
            continue

        # Check if provider is enabled
        if provider_name == "open-meteo" and not settings.enable_open_meteo:
            continue
        if provider_name == "metno" and not settings.enable_metno:
            continue
        if provider_name == "openweather" and not settings.enable_openweather:
            continue

        try:
            provider = PROVIDERS[provider_name]
            data = await provider.fetch_forecast(lat, lon, hours, include)
            results.extend(data)
        except Exception as e:
            logger.error(f"Failed to fetch from {provider_name}: {e}")

    return results
