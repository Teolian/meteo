"""Database models using SQLModel."""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class WaterbodyDB(SQLModel, table=True):
    """Waterbody database model."""
    __tablename__ = "waterbodies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    lat: float
    lon: float
    region: str = Field(index=True)
    type: str  # reservoir, lake, river


class ForecastHourlyDB(SQLModel, table=True):
    """Hourly forecast database model."""
    __tablename__ = "forecast_hourly"

    id: Optional[int] = Field(default=None, primary_key=True)
    wb_id: int = Field(foreign_key="waterbodies.id", index=True)
    time: datetime = Field(index=True)
    provider: str
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
    created_at: datetime = Field(default_factory=datetime.now)


class SignalDB(SQLModel, table=True):
    """Signal database model."""
    __tablename__ = "signals"

    id: Optional[int] = Field(default=None, primary_key=True)
    wb_id: int = Field(foreign_key="waterbodies.id", index=True)
    time: datetime = Field(index=True)
    dP6_hpa: Optional[float] = None
    dP12_hpa: Optional[float] = None
    dP24_hpa: Optional[float] = None
    front_like: bool = False
    stable_window: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class BiteMetricDB(SQLModel, table=True):
    """Bite index metrics database model."""
    __tablename__ = "metrics"

    id: Optional[int] = Field(default=None, primary_key=True)
    wb_id: int = Field(foreign_key="waterbodies.id", index=True)
    time: datetime = Field(index=True)
    score: int
    species_mask: str  # JSON array of species
    confidence: str
    explain_json: str  # JSON array of explanations
    created_at: datetime = Field(default_factory=datetime.now)
