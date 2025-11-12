"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# Forecast schemas
class ForecastMeta(BaseModel):
    """Forecast metadata."""
    lat: float
    lon: float
    timezone: str = "Europe/Moscow"
    providers: List[str]


class HourlyForecast(BaseModel):
    """Hourly forecast data point."""
    time: str  # ISO 8601 with timezone
    mslp_hpa: Optional[float] = None
    surface_pressure_hpa: Optional[float] = None
    t2m_c: Optional[float] = None
    wind10_mps: Optional[float] = None
    wind_dir_deg: Optional[int] = None
    gust_mps: Optional[float] = None
    cloud_pct: Optional[int] = None
    precip_mm: Optional[float] = None
    snowfall_mm: Optional[float] = None
    snow_depth_cm: Optional[float] = None
    visibility_km: Optional[float] = None
    provider: str


class ForecastResponse(BaseModel):
    """Forecast API response."""
    meta: ForecastMeta
    hourly: List[HourlyForecast]


# Signals schemas
class PressureTrend(BaseModel):
    """Pressure trend data."""
    dP6_hpa: Optional[float] = None
    dP12_hpa: Optional[float] = None
    dP24_hpa: Optional[float] = None


class SignalFlag(BaseModel):
    """Signal flag for specific time."""
    time: str
    front_like: Optional[bool] = False
    stable_window: Optional[bool] = False
    reason: Optional[List[str]] = []


class SignalsResponse(BaseModel):
    """Signals API response."""
    trend: PressureTrend
    flags: List[SignalFlag]


# Bite index schemas
class BiteIndexMeta(BaseModel):
    """Bite index metadata."""
    species: List[str]


class BiteIndexHourly(BaseModel):
    """Bite index for specific hour."""
    time: str
    score: int = Field(..., ge=0, le=100)
    explain: List[str]


class BiteIndexResponse(BaseModel):
    """Bite index API response."""
    meta: BiteIndexMeta
    hourly: List[BiteIndexHourly]
    confidence: Literal["low", "medium", "high"]


# Waterbody schemas
class WaterbodyBase(BaseModel):
    """Base waterbody schema."""
    name: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    region: str
    type: str  # reservoir, lake, river


class WaterbodyCreate(WaterbodyBase):
    """Schema for creating waterbody."""
    pass


class WaterbodyUpdate(BaseModel):
    """Schema for updating waterbody."""
    name: Optional[str] = None
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    region: Optional[str] = None
    type: Optional[str] = None


class Waterbody(WaterbodyBase):
    """Waterbody schema with ID."""
    id: int

    class Config:
        from_attributes = True
