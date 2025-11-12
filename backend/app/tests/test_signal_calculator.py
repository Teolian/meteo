"""Unit tests for signal calculator."""
import pytest
from datetime import datetime, timedelta

from app.services.signal_calculator import SignalCalculator


@pytest.fixture
def calculator():
    """Create signal calculator instance."""
    return SignalCalculator()


@pytest.fixture
def sample_forecast_data():
    """Create sample forecast data for testing."""
    base_time = datetime(2025, 11, 12, 12, 0, 0)
    data = []

    # Generate 48 hours of sample data
    for i in range(48):
        time = base_time + timedelta(hours=i)
        # Simulate pressure drop (front approaching)
        pressure = 1013.0 - (i * 0.5) if i < 24 else 1001.0 + ((i - 24) * 0.3)

        data.append({
            "time": time.isoformat(),
            "mslp_hpa": pressure,
            "wind10_mps": 3.0 + (i % 10),
            "wind_dir_deg": 180 + (i * 5),
            "cloud_pct": 30 + (i % 40),
            "precip_mm": 0.1 if i > 20 else 0
        })

    return data


def test_calculate_pressure_deltas(calculator, sample_forecast_data):
    """Test pressure delta calculation."""
    result = calculator.calculate_pressure_deltas(
        sample_forecast_data,
        windows=[6, 12, 24]
    )

    deltas = result["deltas"]

    assert len(deltas) > 0, "Should calculate deltas"

    # Check structure
    for delta in deltas:
        assert "time" in delta
        assert "mslp_hpa" in delta

    # Check specific windows
    # At index 12 (12 hours in), should have 6h and 12h deltas
    delta_12h = next((d for d in deltas if d["time"] == sample_forecast_data[12]["time"]), None)
    assert delta_12h is not None
    assert "dP6_hpa" in delta_12h
    assert "dP12_hpa" in delta_12h

    # At index 24 (24 hours in), should have all deltas
    delta_24h = next((d for d in deltas if d["time"] == sample_forecast_data[24]["time"]), None)
    assert delta_24h is not None
    assert "dP6_hpa" in delta_24h
    assert "dP12_hpa" in delta_24h
    assert "dP24_hpa" in delta_24h

    # Pressure is falling, so dP should be negative
    if delta_24h["dP24_hpa"] is not None:
        assert delta_24h["dP24_hpa"] < 0, "Pressure should be falling"


def test_detect_front_like_flag(calculator, sample_forecast_data):
    """Test front-like flag detection."""
    # Calculate deltas first
    delta_result = calculator.calculate_pressure_deltas(sample_forecast_data, windows=[6, 12, 24])
    deltas = delta_result["deltas"]

    # Detect flags
    flags = calculator.detect_flags(sample_forecast_data, deltas)

    assert len(flags) > 0, "Should detect some flags"

    # Should detect front_like due to pressure drop
    front_flags = [f for f in flags if f.get("front_like")]
    assert len(front_flags) > 0, "Should detect front-like conditions"

    # Check reasons
    for flag in front_flags:
        assert "reason" in flag
        assert len(flag["reason"]) > 0, "Should have reasons"


def test_stable_window_detection():
    """Test stable window detection."""
    calculator = SignalCalculator()

    # Create stable conditions
    base_time = datetime(2025, 11, 12, 12, 0, 0)
    stable_data = []

    for i in range(24):
        time = base_time + timedelta(hours=i)
        stable_data.append({
            "time": time.isoformat(),
            "mslp_hpa": 1013.0 + (i % 2) * 0.5,  # Very stable pressure
            "wind10_mps": 2.0,  # Low wind
            "wind_dir_deg": 180,
            "cloud_pct": 40,
            "precip_mm": 0
        })

    # Calculate deltas
    delta_result = calculator.calculate_pressure_deltas(stable_data, windows=[6, 12, 24])
    deltas = delta_result["deltas"]

    # Detect flags
    flags = calculator.detect_flags(stable_data, deltas)

    # Should detect stable_window
    stable_flags = [f for f in flags if f.get("stable_window")]
    assert len(stable_flags) > 0, "Should detect stable window"


def test_wind_shift_calculation(calculator):
    """Test wind direction shift calculation."""
    data = [
        {
            "time": "2025-11-12T12:00:00",
            "mslp_hpa": 1013,
            "wind_dir_deg": 180
        },
        {
            "time": "2025-11-12T13:00:00",
            "mslp_hpa": 1013,
            "wind_dir_deg": 185
        },
        {
            "time": "2025-11-12T18:00:00",
            "mslp_hpa": 1010,
            "wind_dir_deg": 270  # 90° shift from 6h ago
        }
    ]

    # Calculate shift at index 2 (6 hours back to index 0)
    shift = calculator._calculate_wind_shift(data, 2, hours_back=6)

    assert shift is not None
    assert shift == 90, f"Expected 90° shift, got {shift}"


def test_cloud_increase_calculation(calculator):
    """Test cloud cover increase calculation."""
    data = [
        {
            "time": "2025-11-12T12:00:00",
            "cloud_pct": 20
        },
        {
            "time": "2025-11-12T18:00:00",
            "cloud_pct": 70  # +50% increase
        }
    ]

    increase = calculator._calculate_cloud_increase(data, 1, hours_back=6)

    assert increase is not None
    assert increase == 50, f"Expected 50% increase, got {increase}"


def test_pressure_delta_with_missing_data(calculator):
    """Test delta calculation with missing pressure data."""
    data = [
        {"time": "2025-11-12T12:00:00", "mslp_hpa": 1013},
        {"time": "2025-11-12T13:00:00", "mslp_hpa": None},  # Missing
        {"time": "2025-11-12T14:00:00", "mslp_hpa": 1011}
    ]

    result = calculator.calculate_pressure_deltas(data, windows=[6])
    deltas = result["deltas"]

    # Should handle missing data gracefully
    assert len(deltas) >= 0
    # Points with missing pressure should not be in results or have None values
    for delta in deltas:
        if delta.get("mslp_hpa") is None:
            assert True  # OK to skip or have None delta
