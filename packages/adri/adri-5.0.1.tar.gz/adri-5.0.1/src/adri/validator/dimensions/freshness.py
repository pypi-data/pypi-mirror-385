"""Freshness dimension assessor for the ADRI validation framework.

This module contains the FreshnessAssessor class that evaluates data freshness
(recency and temporal relevance) according to requirements defined in ADRI standards.
"""

from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from ...core.protocols import DimensionAssessor


class FreshnessAssessor(DimensionAssessor):
    """Assesses data freshness (recency and temporal relevance).

    The freshness assessor evaluates whether data is current and up-to-date
    based on configured recency windows and date field constraints.
    """

    def get_dimension_name(self) -> str:
        """Get the name of this dimension."""
        return "freshness"

    def assess(self, data: Any, requirements: Dict[str, Any]) -> float:
        """Assess freshness dimension for the given data.

        Args:
            data: The data to assess (typically a pandas DataFrame)
            requirements: The dimension-specific requirements from the standard

        Returns:
            A score between 0.0 and 20.0 representing the freshness quality
        """
        if not isinstance(data, pd.DataFrame):
            return 20.0  # Perfect score for non-DataFrame data

        if data.empty:
            return 20.0  # Perfect score for empty data

        # Get freshness configuration
        freshness_config = self._extract_freshness_config(requirements)
        if not freshness_config["is_active"]:
            return 20.0  # Perfect score when no freshness configured

        return self._assess_freshness_with_config(data, freshness_config)

    def _extract_freshness_config(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract freshness configuration from requirements."""
        # Check if freshness rules are active
        scoring_cfg = requirements.get("scoring", {})
        rule_weights_cfg = scoring_cfg.get("rule_weights", {}) if scoring_cfg else {}

        recency_weight = 0.0
        try:
            recency_weight = float(rule_weights_cfg.get("recency_window", 0.0))
        except Exception:
            recency_weight = 0.0
        if recency_weight < 0.0:
            recency_weight = 0.0

        # Get freshness metadata
        metadata = requirements.get("metadata", {})
        freshness_meta = (
            metadata.get("freshness", {}) if isinstance(metadata, dict) else {}
        )

        as_of_str = freshness_meta.get("as_of")
        date_field = freshness_meta.get("date_field")
        window_days = freshness_meta.get("window_days")

        # Validate configuration
        window_days_val = None
        try:
            window_days_val = float(window_days) if window_days is not None else None
        except Exception:
            window_days_val = None

        has_metadata = bool(as_of_str and date_field and window_days_val is not None)
        is_active = has_metadata and recency_weight > 0.0

        return {
            "is_active": is_active,
            "has_metadata": has_metadata,
            "recency_weight": recency_weight,
            "as_of_str": as_of_str,
            "date_field": date_field,
            "window_days": window_days_val,
        }

    def _assess_freshness_with_config(
        self, data: pd.DataFrame, config: Dict[str, Any]
    ) -> float:
        """Assess freshness using the extracted configuration."""
        # Parse the as_of date
        as_of = self._parse_as_of_date(config["as_of_str"])
        if as_of is None:
            return 20.0  # Perfect score for invalid date

        date_field = config["date_field"]
        window_days = config["window_days"]

        # Check if the date field exists
        if date_field not in data.columns:
            return 20.0  # Perfect score when field not found

        # Parse date values in the specified field
        series = data[date_field]
        parsed_dates = pd.to_datetime(series, utc=True, errors="coerce")

        # Convert to naive datetime to match as_of
        try:
            parsed_dates = parsed_dates.dt.tz_convert(None)
        except Exception:
            pass  # Already naive or conversion failed

        # Count valid (parseable) dates
        total_valid_dates = int(parsed_dates.notna().sum())
        if total_valid_dates <= 0:
            return 20.0  # Perfect score for unparseable dates

        # Check recency: count dates within the window
        deltas = as_of - parsed_dates
        days_diff = deltas.dt.days

        # Records are fresh if they are within the window (days_diff <= window_days)
        # Future-dated records (days_diff < 0) are also considered fresh
        fresh_mask = (days_diff <= window_days) | (days_diff < 0)
        fresh_count = int(fresh_mask.sum())

        # Calculate pass rate and score
        pass_rate = (fresh_count / total_valid_dates) if total_valid_dates > 0 else 1.0
        score = float(pass_rate * 20.0)

        return score

    def _parse_as_of_date(self, as_of_str: Optional[str]) -> Optional[datetime]:
        """Parse the as_of date string into a datetime object."""
        if not as_of_str:
            return None

        try:
            as_of = pd.to_datetime(as_of_str, utc=True, errors="coerce")
            if as_of is not None and not pd.isna(as_of):
                try:
                    # Convert to naive datetime
                    return as_of.tz_convert(None).to_pydatetime()
                except Exception:
                    # Already naive or conversion failed
                    return as_of.to_pydatetime()
        except Exception:
            pass

        return None

    def get_freshness_breakdown(
        self, data: pd.DataFrame, requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get detailed freshness breakdown for reporting.

        Args:
            data: DataFrame to analyze
            requirements: Requirements from standard

        Returns:
            Detailed breakdown including freshness statistics
        """
        config = self._extract_freshness_config(requirements)

        if not config["is_active"]:
            return {
                "date_field": config.get("date_field"),
                "as_of": config.get("as_of_str"),
                "window_days": config.get("window_days"),
                "counts": {"passed": 0, "total": 0},
                "pass_rate": 1.0,
                "rule_weights_applied": {"recency_window": config["recency_weight"]},
                "score_0_20": 19.0,
                "warnings": [
                    "freshness checking not configured or inactive; using baseline score 19.0/20"
                ],
            }

        as_of = self._parse_as_of_date(config["as_of_str"])
        date_field = config["date_field"]
        window_days = config["window_days"]

        if as_of is None:
            return {
                "date_field": date_field,
                "as_of": config["as_of_str"],
                "window_days": int(window_days) if window_days is not None else None,
                "counts": {"passed": 0, "total": 0},
                "pass_rate": 1.0,
                "rule_weights_applied": {"recency_window": config["recency_weight"]},
                "score_0_20": 19.0,
                "warnings": ["invalid as_of timestamp; using baseline score 19.0/20"],
            }

        if date_field not in data.columns:
            return {
                "date_field": date_field,
                "as_of": str(as_of),
                "window_days": int(window_days) if window_days is not None else None,
                "counts": {"passed": 0, "total": 0},
                "pass_rate": 1.0,
                "rule_weights_applied": {"recency_window": config["recency_weight"]},
                "score_0_20": 19.0,
                "warnings": [
                    f"date_field '{date_field}' not found, using baseline score 19.0/20"
                ],
            }

        # Parse and analyze dates
        series = data[date_field]
        parsed_dates = pd.to_datetime(series, utc=True, errors="coerce")

        try:
            parsed_dates = parsed_dates.dt.tz_convert(None)
        except Exception:
            pass

        total_valid = int(parsed_dates.notna().sum())

        if total_valid <= 0:
            return {
                "date_field": date_field,
                "as_of": str(as_of),
                "window_days": int(window_days) if window_days is not None else None,
                "counts": {"passed": 0, "total": 0},
                "pass_rate": 1.0,
                "rule_weights_applied": {"recency_window": config["recency_weight"]},
                "score_0_20": 19.0,
                "warnings": [
                    "no parseable dates in date_field; using baseline score 19.0/20"
                ],
            }

        # Calculate freshness
        deltas = as_of - parsed_dates
        days_diff = deltas.dt.days
        fresh_mask = (days_diff <= window_days) | (days_diff < 0)
        fresh_count = int(fresh_mask.sum())

        pass_rate = (fresh_count / total_valid) if total_valid > 0 else 1.0
        score = float(pass_rate * 20.0)

        return {
            "date_field": date_field,
            "as_of": str(as_of),
            "window_days": int(window_days) if window_days is not None else None,
            "counts": {"passed": fresh_count, "total": total_valid},
            "pass_rate": pass_rate,
            "rule_weights_applied": {"recency_window": config["recency_weight"]},
            "score_0_20": score,
        }

    def assess_with_config(
        self, data: pd.DataFrame, freshness_config: Dict[str, Any]
    ) -> float:
        """Assess freshness with explicit configuration for backward compatibility.

        Args:
            data: DataFrame to assess
            freshness_config: Configuration containing date_fields etc.

        Returns:
            Freshness score between 0.0 and 20.0
        """
        # Handle legacy format
        date_fields = freshness_config.get("date_fields", [])
        if date_fields:
            # Simple freshness check - return good score if date fields exist
            valid_date_fields = [
                field for field in date_fields if field in data.columns
            ]
            if valid_date_fields:
                return 20.0

        return 20.0  # Perfect baseline score
