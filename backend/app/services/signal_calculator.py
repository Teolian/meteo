"""Signal calculation logic for pressure trends and weather flags."""
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SignalCalculator:
    """Calculate weather signals and flags."""

    # Default thresholds
    DEFAULT_THRESHOLDS = {
        "front_pressure_drop_hpa": -4.0,  # Rapid pressure drop indicator
        "front_pressure_rise_hpa": 4.0,   # Rapid pressure rise indicator
        "front_wind_shift_deg": 45,       # Wind direction change
        "front_cloud_increase_pct": 20,   # Cloud cover increase
        "stable_pressure_threshold_hpa": 2.0,  # Max ΔP for stability
        "stable_wind_threshold_mps": 5.0,      # Max wind for stability
        "stable_window_hours": 12              # Minimum hours for stable window
    }

    def __init__(self, thresholds: Optional[Dict] = None):
        """Initialize with custom thresholds."""
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()
        if thresholds:
            self.thresholds.update(thresholds)

    def calculate_pressure_deltas(
        self,
        forecast_data: List[Dict],
        windows: List[int] = [6, 12, 24]
    ) -> Dict[str, List[Dict]]:
        """
        Calculate pressure deltas (ΔP) for given time windows.

        Args:
            forecast_data: List of forecast points with time and mslp_hpa
            windows: List of window sizes in hours [6, 12, 24]

        Returns:
            Dict with pressure trends per time point
        """
        # Sort by time
        sorted_data = sorted(forecast_data, key=lambda x: x["time"])

        results = []

        for i, current in enumerate(sorted_data):
            current_time = self._parse_time(current["time"])
            current_pressure = current.get("mslp_hpa")

            if current_pressure is None:
                continue

            deltas = {
                "time": current["time"],
                "mslp_hpa": current_pressure
            }

            # Calculate delta for each window
            for window in windows:
                target_time = current_time - timedelta(hours=window)
                past_pressure = self._find_pressure_at_time(sorted_data, target_time)

                if past_pressure is not None:
                    delta = current_pressure - past_pressure
                    deltas[f"dP{window}_hpa"] = round(delta, 2)
                else:
                    deltas[f"dP{window}_hpa"] = None

            results.append(deltas)

        return {"deltas": results}

    def detect_flags(
        self,
        forecast_data: List[Dict],
        deltas: List[Dict]
    ) -> List[Dict]:
        """
        Detect weather flags (front_like, stable_window).

        Args:
            forecast_data: Original forecast data with all weather params
            deltas: Pressure delta data from calculate_pressure_deltas

        Returns:
            List of flag events with reasons
        """
        flags = []

        # Create lookup for deltas
        delta_map = {d["time"]: d for d in deltas}

        # Sort forecast data
        sorted_data = sorted(forecast_data, key=lambda x: x["time"])

        for i, current in enumerate(sorted_data):
            time_str = current["time"]
            current_time = self._parse_time(time_str)

            # Get deltas for this time
            delta_data = delta_map.get(time_str, {})
            dP6 = delta_data.get("dP6_hpa")
            dP12 = delta_data.get("dP12_hpa")

            if dP6 is None or dP12 is None:
                continue

            # Check for front-like conditions
            front_reasons = []

            # Rapid pressure change
            if dP12 <= self.thresholds["front_pressure_drop_hpa"]:
                front_reasons.append(f"dP12<{self.thresholds['front_pressure_drop_hpa']}")
            elif dP12 >= self.thresholds["front_pressure_rise_hpa"]:
                front_reasons.append(f"dP12>{self.thresholds['front_pressure_rise_hpa']}")

            # Wind shift
            if i > 0:
                wind_shift = self._calculate_wind_shift(sorted_data, i, hours_back=6)
                if wind_shift and wind_shift >= self.thresholds["front_wind_shift_deg"]:
                    front_reasons.append(f"wind_shift>{self.thresholds['front_wind_shift_deg']}°")

            # Cloud/precip increase
            if i > 0:
                cloud_increase = self._calculate_cloud_increase(sorted_data, i, hours_back=6)
                if cloud_increase and cloud_increase >= self.thresholds["front_cloud_increase_pct"]:
                    front_reasons.append("cloud+precip↑")

            if front_reasons:
                flags.append({
                    "time": time_str,
                    "front_like": True,
                    "stable_window": False,
                    "reason": front_reasons
                })

            # Check for stable window
            stable = self._check_stable_window(
                sorted_data,
                delta_map,
                i,
                window_hours=self.thresholds["stable_window_hours"]
            )

            if stable:
                flags.append({
                    "time": time_str,
                    "front_like": False,
                    "stable_window": True,
                    "reason": ["stable pressure+wind"]
                })

        return flags

    def _find_pressure_at_time(
        self,
        data: List[Dict],
        target_time: datetime
    ) -> Optional[float]:
        """Find pressure value closest to target time."""
        closest = None
        min_diff = timedelta(hours=2)  # Max 2-hour tolerance

        for point in data:
            point_time = self._parse_time(point["time"])
            diff = abs(point_time - target_time)

            if diff < min_diff:
                min_diff = diff
                closest = point.get("mslp_hpa")

        return closest

    def _calculate_wind_shift(
        self,
        data: List[Dict],
        current_idx: int,
        hours_back: int = 6
    ) -> Optional[float]:
        """Calculate wind direction shift over hours_back."""
        current = data[current_idx]
        current_time = self._parse_time(current["time"])
        current_dir = current.get("wind_dir_deg")

        if current_dir is None:
            return None

        # Find past point
        target_time = current_time - timedelta(hours=hours_back)
        past_dir = None

        for point in data[:current_idx]:
            point_time = self._parse_time(point["time"])
            if abs(point_time - target_time) < timedelta(hours=1):
                past_dir = point.get("wind_dir_deg")
                break

        if past_dir is None:
            return None

        # Calculate smallest angle difference
        diff = abs(current_dir - past_dir)
        if diff > 180:
            diff = 360 - diff

        return diff

    def _calculate_cloud_increase(
        self,
        data: List[Dict],
        current_idx: int,
        hours_back: int = 6
    ) -> Optional[float]:
        """Calculate cloud cover increase over hours_back."""
        current = data[current_idx]
        current_time = self._parse_time(current["time"])
        current_cloud = current.get("cloud_pct")

        if current_cloud is None:
            return None

        # Find past point
        target_time = current_time - timedelta(hours=hours_back)
        past_cloud = None

        for point in data[:current_idx]:
            point_time = self._parse_time(point["time"])
            if abs(point_time - target_time) < timedelta(hours=1):
                past_cloud = point.get("cloud_pct")
                break

        if past_cloud is None:
            return None

        return current_cloud - past_cloud

    def _check_stable_window(
        self,
        data: List[Dict],
        delta_map: Dict,
        current_idx: int,
        window_hours: int = 12
    ) -> bool:
        """Check if conditions have been stable for window_hours."""
        current = data[current_idx]
        current_time = self._parse_time(current["time"])

        # Check past window_hours
        stable_count = 0
        required_points = window_hours // 2  # At least half the window should be stable

        for point in data[max(0, current_idx - window_hours):current_idx + 1]:
            point_time = self._parse_time(point["time"])
            if (current_time - point_time).total_seconds() / 3600 > window_hours:
                continue

            # Check pressure stability
            delta_data = delta_map.get(point["time"], {})
            dP6 = delta_data.get("dP6_hpa")

            if dP6 is not None and abs(dP6) <= self.thresholds["stable_pressure_threshold_hpa"]:
                # Check wind stability
                wind_speed = point.get("wind10_mps")
                if wind_speed is not None and wind_speed <= self.thresholds["stable_wind_threshold_mps"]:
                    stable_count += 1

        return stable_count >= required_points

    @staticmethod
    def _parse_time(time_str: str) -> datetime:
        """Parse ISO time string to datetime."""
        try:
            # Handle timezone-aware strings
            if "+" in time_str or time_str.endswith("Z"):
                return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            return datetime.fromisoformat(time_str)
        except Exception as e:
            logger.error(f"Error parsing time {time_str}: {e}")
            raise
