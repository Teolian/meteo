"""Bite index calculator (v0 formula)."""
import logging
import math
from datetime import datetime
from typing import Dict, List, Literal, Optional

logger = logging.getLogger(__name__)


class BiteIndexCalculator:
    """Calculate bite index based on weather conditions."""

    # Default weights
    DEFAULT_WEIGHTS = {
        "w_stab": 0.35,    # Pressure stability
        "w_front": 0.25,   # Front signals
        "w_wind": 0.15,    # Wind conditions
        "w_cloud": 0.10,   # Cloud cover
        "w_snow": 0.10,    # Snow/precipitation
        "w_pref": 0.05     # Species preference
    }

    # Species-specific preferences
    SPECIES_PROFILES = {
        "pike": {
            "prefers_falling_pressure": True,
            "tolerates_cold": True,
            "prefers_low_wind": True,
            "optimal_temp_range": (-5, 5),
            "active_hours": list(range(8, 17))  # 8am-5pm
        },
        "walleye": {
            "prefers_falling_pressure": False,
            "tolerates_cold": True,
            "prefers_low_wind": False,
            "optimal_temp_range": (-10, 0),
            "active_hours": list(range(0, 24))  # Active day and night
        },
        "perch": {
            "prefers_falling_pressure": False,
            "tolerates_cold": True,
            "prefers_low_wind": True,
            "optimal_temp_range": (-5, 5),
            "active_hours": list(range(8, 17))  # Daytime feeder
        },
        "bream": {
            "prefers_falling_pressure": False,
            "tolerates_cold": False,
            "prefers_low_wind": True,
            "optimal_temp_range": (0, 10),
            "active_hours": list(range(10, 16))  # Midday
        }
    }

    def __init__(self, weights: Optional[Dict] = None):
        """Initialize with custom weights."""
        self.weights = self.DEFAULT_WEIGHTS.copy()
        if weights:
            self.weights.update(weights)

    def calculate_index(
        self,
        forecast_data: List[Dict],
        deltas: List[Dict],
        flags: List[Dict],
        species: List[str] = ["pike", "perch"]
    ) -> Dict:
        """
        Calculate bite index for each hour.

        Args:
            forecast_data: Weather forecast data
            deltas: Pressure delta data
            flags: Signal flags (front_like, stable_window)
            species: List of target species

        Returns:
            Dict with hourly bite index scores and confidence
        """
        # Create lookups
        delta_map = {d["time"]: d for d in deltas}
        flag_map = {f["time"]: f for f in flags}

        results = []

        for point in forecast_data:
            time_str = point["time"]
            delta_data = delta_map.get(time_str, {})
            flag_data = flag_map.get(time_str, {})

            # Calculate component scores
            s_stab = self._score_stability(delta_data)
            s_front = self._score_front(delta_data, flag_data)
            s_wind = self._score_wind(point)
            s_cloud = self._score_cloud(point)
            s_snow = self._score_snow(point)
            s_pref = self._score_species_preference(point, species)

            # Weighted sum
            score = (
                self.weights["w_stab"] * s_stab +
                self.weights["w_front"] * s_front +
                self.weights["w_wind"] * s_wind +
                self.weights["w_cloud"] * s_cloud +
                self.weights["w_snow"] * s_snow +
                self.weights["w_pref"] * s_pref
            )

            # Normalize to 0-100
            score = max(0, min(100, int(score)))

            # Generate explanation
            explain = self._generate_explanation(
                s_stab, s_front, s_wind, s_cloud, s_snow, s_pref,
                point, delta_data, flag_data
            )

            results.append({
                "time": time_str,
                "score": score,
                "explain": explain
            })

        # Calculate confidence
        confidence = self._calculate_confidence(forecast_data, deltas)

        return {
            "hourly": results,
            "confidence": confidence
        }

    def _score_stability(self, delta_data: Dict) -> float:
        """
        Score pressure stability (0-100).
        Low |ΔP| = high score.
        """
        dP12 = delta_data.get("dP12_hpa")
        if dP12 is None:
            return 50.0  # Neutral score if no data

        # Optimal: |ΔP12| < 2 hPa
        # Poor: |ΔP12| > 6 hPa
        abs_dp = abs(dP12)

        if abs_dp < 2:
            return 100.0
        elif abs_dp < 4:
            return 80.0
        elif abs_dp < 6:
            return 50.0
        else:
            return 20.0

    def _score_front(self, delta_data: Dict, flag_data: Dict) -> float:
        """
        Score frontal conditions (0-100).
        Pre-front (gradual drop) = bonus
        Front active = penalty
        """
        dP12 = delta_data.get("dP12_hpa")
        front_like = flag_data.get("front_like", False)
        stable_window = flag_data.get("stable_window", False)

        # Stable window = high score
        if stable_window:
            return 100.0

        # Front active = low score
        if front_like:
            return 20.0

        # Pre-front: gradual pressure drop (-2 to -4 hPa)
        if dP12 and -4 < dP12 < -2:
            return 85.0  # Good "feeding before storm" window

        return 50.0  # Neutral

    def _score_wind(self, point: Dict) -> float:
        """
        Score wind conditions (0-100).
        Low wind = better fishing.
        """
        wind_speed = point.get("wind10_mps")
        gust = point.get("gust_mps")

        if wind_speed is None:
            return 50.0

        # Optimal: < 3 m/s
        # Poor: > 8 m/s or strong gusts
        if wind_speed < 3:
            score = 100.0
        elif wind_speed < 5:
            score = 80.0
        elif wind_speed < 8:
            score = 50.0
        else:
            score = 30.0

        # Penalty for strong gusts
        if gust and gust > 10:
            score *= 0.7

        return score

    def _score_cloud(self, point: Dict) -> float:
        """
        Score cloud cover (0-100).
        Moderate clouds = best (light under ice).
        """
        cloud_pct = point.get("cloud_pct")

        if cloud_pct is None:
            return 50.0

        # Optimal: 30-70% (some light, not too dark)
        # Poor: Very clear or very overcast
        if 30 <= cloud_pct <= 70:
            return 90.0
        elif 20 <= cloud_pct <= 80:
            return 70.0
        elif cloud_pct < 20:
            return 60.0  # Very clear can be ok
        else:
            return 40.0  # Very dark

    def _score_snow(self, point: Dict) -> float:
        """
        Score snow/precipitation (0-100).
        Light snow OK, heavy snow/storm bad.
        """
        snowfall = point.get("snowfall_mm", 0) or 0
        precip = point.get("precip_mm", 0) or 0

        total_precip = snowfall + precip

        # No precip = good
        if total_precip < 0.5:
            return 90.0
        # Light snow = OK
        elif total_precip < 2:
            return 70.0
        # Moderate snow = questionable
        elif total_precip < 5:
            return 40.0
        # Heavy snow = poor
        else:
            return 20.0

    def _score_species_preference(self, point: Dict, species: List[str]) -> float:
        """
        Score based on species-specific preferences (0-100).
        """
        if not species:
            return 50.0

        scores = []

        for sp in species:
            if sp not in self.SPECIES_PROFILES:
                continue

            profile = self.SPECIES_PROFILES[sp]
            sp_score = 50.0

            # Temperature preference
            temp = point.get("t2m_c")
            if temp:
                opt_min, opt_max = profile["optimal_temp_range"]
                if opt_min <= temp <= opt_max:
                    sp_score += 20
                elif temp < opt_min - 10 or temp > opt_max + 10:
                    sp_score -= 20

            # Time of day
            try:
                time_obj = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
                hour = time_obj.hour
                if hour in profile["active_hours"]:
                    sp_score += 15
            except:
                pass

            scores.append(sp_score)

        return sum(scores) / len(scores) if scores else 50.0

    def _generate_explanation(
        self,
        s_stab: float,
        s_front: float,
        s_wind: float,
        s_cloud: float,
        s_snow: float,
        s_pref: float,
        point: Dict,
        delta_data: Dict,
        flag_data: Dict
    ) -> List[str]:
        """Generate human-readable explanation of score."""
        explain = []

        # Pressure
        if s_stab >= 80:
            explain.append("stable pressure")
        elif s_stab <= 30:
            explain.append("unstable pressure")

        # Front
        if flag_data.get("stable_window"):
            explain.append("stable window")
        elif flag_data.get("front_like"):
            explain.append("front approaching")
        else:
            dP12 = delta_data.get("dP12_hpa")
            if dP12 and -4 < dP12 < -2:
                explain.append("pre-front feeding")

        # Wind
        wind = point.get("wind10_mps")
        if wind and wind < 3:
            explain.append("low wind")
        elif wind and wind > 8:
            explain.append("strong wind")

        # Cloud
        cloud = point.get("cloud_pct")
        if cloud and 30 <= cloud <= 70:
            explain.append("good light")

        # Snow
        snow = point.get("snowfall_mm", 0) or 0
        if 0.5 < snow < 2:
            explain.append("light snow")
        elif snow >= 5:
            explain.append("heavy snow")

        if not explain:
            explain.append("moderate conditions")

        return explain

    def _calculate_confidence(
        self,
        forecast_data: List[Dict],
        deltas: List[Dict]
    ) -> Literal["low", "medium", "high"]:
        """
        Calculate confidence based on data availability and variability.
        """
        # Check data completeness
        total_points = len(forecast_data)
        complete_points = sum(
            1 for p in forecast_data
            if p.get("mslp_hpa") and p.get("wind10_mps") and p.get("t2m_c")
        )

        completeness = complete_points / total_points if total_points > 0 else 0

        # Check pressure variability (high variability = lower confidence)
        pressures = [d.get("dP12_hpa") for d in deltas if d.get("dP12_hpa")]
        if pressures:
            variance = sum((abs(p) - sum(map(abs, pressures)) / len(pressures)) ** 2 for p in pressures) / len(pressures)
            variability = math.sqrt(variance)
        else:
            variability = 0

        # Determine confidence
        if completeness > 0.9 and variability < 3:
            return "high"
        elif completeness > 0.7 and variability < 5:
            return "medium"
        else:
            return "low"
