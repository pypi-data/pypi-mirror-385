"""Field inference engine for ADRI standard generation.

This module contains the FieldInferenceEngine class that handles field-level
inference including type detection, constraint generation, and rule creation
for individual data fields.
"""

from typing import Any

import pandas as pd

from ..rule_inference import (
    infer_allowed_values,
    infer_allowed_values_tolerant,
    infer_date_bounds,
    infer_length_bounds,
    infer_numeric_range,
    infer_numeric_range_robust,
    infer_regex_pattern,
    InferenceConfig,
)


class FieldInferenceEngine:
    """Handles inference of field-level requirements and constraints.

    The FieldInferenceEngine focuses specifically on analyzing individual fields
    to generate type information, nullability rules, and field-specific constraints
    like patterns, ranges, and allowed values.
    """

    def __init__(self):
        """Initialize the field inference engine."""

    def infer_field_requirements(
        self,
        data: pd.DataFrame,
        field_profile: dict[str, Any],
        config: InferenceConfig,
        pk_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Infer comprehensive requirements for all fields in the data.

        Args:
            data: DataFrame containing the data to analyze
            field_profile: Profile data for all fields from DataProfiler
            config: Inference configuration settings
            pk_fields: Primary key field names to suppress enum generation

        Returns:
            Dictionary mapping field names to their requirements
        """
        field_requirements = {}
        prof_fields = field_profile.get("fields", {}) or {}

        for col in data.columns:
            field_prof = prof_fields.get(col, {"dtype": str(data[col].dtype)})
            field_prof.setdefault("name", col)

            field_requirements[col] = self.build_field_requirement(
                field_prof, data[col], config, pk_fields=pk_fields
            )

        return field_requirements

    def build_field_requirement(
        self,
        field_profile: dict[str, Any],
        series: pd.Series,
        config: InferenceConfig,
        pk_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Construct comprehensive field requirement using inference utilities.

        Args:
            field_profile: Profile data for this specific field
            series: Pandas Series containing the field data
            config: Inference configuration settings
            pk_fields: Primary key field names

        Returns:
            Field requirement dictionary with validation_rules format
        """
        req: dict[str, Any] = {}

        # 1) Type and nullability inference
        type_info = self.infer_type_and_nullability(field_profile, series, config)
        req.update(type_info)

        col_name = getattr(series, "name", None)

        # 2) Allowed values (enums) for string/integer fields
        if req.get("type") in ("string", "integer"):
            enum_vals = self.infer_allowed_values(series, config, col_name, pk_fields)
            if enum_vals is not None:
                req["allowed_values"] = enum_vals

        # 3) Type-specific constraint inference
        field_type = req.get("type")
        if field_type in ("integer", "float"):
            bounds = self.infer_numeric_bounds(series, config)
            if bounds:
                req["min_value"], req["max_value"] = bounds[0], bounds[1]

        elif field_type == "string":
            string_constraints = self.infer_string_constraints(series, config)
            req.update(string_constraints)

        elif field_type == "date":
            date_constraints = self.infer_date_bounds(series, config, is_datetime=False)
            req.update(date_constraints)

        elif field_type == "datetime":
            date_constraints = self.infer_date_bounds(series, config, is_datetime=True)
            req.update(date_constraints)

        # 4) Convert constraints to validation_rules format
        field_name_str = str(col_name) if col_name else "field"
        validation_rules = self.convert_field_constraints_to_validation_rules(
            req, field_name_str
        )

        if validation_rules:
            req["validation_rules"] = validation_rules

        return req

    def infer_type_and_nullability(
        self, field_profile: dict[str, Any], series: pd.Series, config: InferenceConfig
    ) -> dict[str, Any]:
        """Infer field type and nullability from profile and data.

        Args:
            field_profile: Profile information for the field
            series: Field data as pandas Series
            config: Inference configuration

        Returns:
            Dictionary with 'type' and 'nullable' keys
        """
        dtype = field_profile.get("dtype", "object")
        common_patterns = field_profile.get("common_patterns", []) or []

        # Attempt numeric coercion for object columns
        treat_as_numeric = False
        try:
            non_null = series.dropna()
            if len(non_null) > 0:
                coerced = pd.to_numeric(non_null, errors="coerce")
                if coerced.notna().all():
                    treat_as_numeric = True
        except Exception:
            treat_as_numeric = False

        # Determine type based on dtype and patterns
        if "int" in dtype and not treat_as_numeric:
            inferred_type = "integer"
        elif ("float" in dtype or treat_as_numeric) and ("bool" not in dtype):
            inferred_type = "float"
        elif "bool" in dtype:
            inferred_type = "boolean"
        elif "datetime" in dtype:
            inferred_type = "datetime"
        elif "date" in common_patterns:
            inferred_type = "date"
        else:
            inferred_type = "string"

        # Determine nullability
        null_count = int(field_profile.get("null_count", 0) or 0)
        nullable = not (null_count == 0)

        return {"type": inferred_type, "nullable": nullable}

    def infer_allowed_values(
        self,
        series: pd.Series,
        config: InferenceConfig,
        col_name: str | None,
        pk_fields: list[str] | None,
    ) -> list[Any] | None:
        """Infer allowed values (enums) for categorical fields.

        Args:
            series: Field data as pandas Series
            config: Inference configuration
            col_name: Column name for ID-like detection
            pk_fields: Primary key fields to suppress enum generation

        Returns:
            List of allowed values or None if not applicable
        """
        # Suppress enum generation for ID-like fields and primary keys
        suppress_enum = False
        if pk_fields and col_name in pk_fields:
            suppress_enum = True
        if self._is_id_like(col_name):
            suppress_enum = True
        if suppress_enum:
            return None

        # Use configured strategy for enum inference
        if getattr(config, "enum_strategy", "coverage") == "tolerant":
            return infer_allowed_values_tolerant(
                series,
                min_coverage=config.enum_min_coverage,
                top_k=getattr(config, "enum_top_k", 10),
                max_unique=config.enum_max_unique,
            )

        return infer_allowed_values(
            series,
            max_unique=config.enum_max_unique,
            min_coverage=config.enum_min_coverage,
        )

    def infer_numeric_bounds(
        self, series: pd.Series, config: InferenceConfig
    ) -> tuple | None:
        """Infer numeric range bounds using configured strategy.

        Args:
            series: Numeric field data
            config: Inference configuration

        Returns:
            Tuple of (min_value, max_value) or None if not applicable
        """
        # Convert to numeric if needed
        try:
            non_null = series.dropna()
            if len(non_null) > 0:
                coerced = pd.to_numeric(non_null, errors="coerce")
                if coerced.notna().all():
                    series_for_range = coerced
                else:
                    series_for_range = series
            else:
                series_for_range = series
        except Exception:
            series_for_range = series

        # Apply configured range strategy
        strategy = getattr(config, "range_strategy", "iqr")
        if strategy == "span":
            rng = infer_numeric_range(
                series_for_range, margin_pct=config.range_margin_pct
            )
        else:
            rng = infer_numeric_range_robust(
                series_for_range,
                strategy=strategy,
                iqr_k=getattr(config, "iqr_k", 1.5),
                quantile_low=getattr(config, "quantile_low", 0.005),
                quantile_high=getattr(config, "quantile_high", 0.995),
                mad_k=getattr(config, "mad_k", 3.0),
            )

        if rng:
            return (float(rng[0]), float(rng[1]))
        return None

    def infer_string_constraints(
        self, series: pd.Series, config: InferenceConfig
    ) -> dict[str, Any]:
        """Infer string-specific constraints like length bounds and patterns.

        Args:
            series: String field data
            config: Inference configuration

        Returns:
            Dictionary with string constraint keys
        """
        constraints: dict[str, Any] = {}

        # Infer length bounds
        try:
            length_bounds = infer_length_bounds(series, widen=None)
            if length_bounds:
                constraints["min_length"] = int(length_bounds[0])
                constraints["max_length"] = int(length_bounds[1])
        except Exception:
            pass

        # Infer regex pattern if enabled
        if getattr(config, "regex_inference_enabled", False):
            try:
                pattern = infer_regex_pattern(series)
                if pattern:
                    constraints["pattern"] = pattern
            except Exception:
                pass

        return constraints

    def infer_date_bounds(
        self, series: pd.Series, config: InferenceConfig, is_datetime: bool = False
    ) -> dict[str, Any]:
        """Infer date/datetime bounds with appropriate field names.

        Args:
            series: Date/datetime field data
            config: Inference configuration
            is_datetime: Whether to use datetime field names vs date field names

        Returns:
            Dictionary with date constraint keys
        """
        constraints: dict[str, Any] = {}

        try:
            date_bounds = infer_date_bounds(series, margin_days=config.date_margin_days)
            if date_bounds:
                if is_datetime:
                    constraints["after_datetime"] = date_bounds[0]
                    constraints["before_datetime"] = date_bounds[1]
                else:
                    constraints["after_date"] = date_bounds[0]
                    constraints["before_date"] = date_bounds[1]
        except Exception:
            pass

        return constraints

    def _is_id_like(self, name: str | None) -> bool:
        """Heuristic to detect ID-like column names to suppress enum generation.

        Args:
            name: Column name to check

        Returns:
            True if the name appears to be ID-like
        """
        if not name:
            return False

        lname = str(name).lower()
        id_tokens = ["id", "key", "code", "number", "num", "uuid", "guid"]

        return any(token in lname for token in id_tokens)

    def validate_field_against_rules(
        self, value: Any, field_req: dict[str, Any]
    ) -> str | None:
        """Validate a single value against field requirements.

        Args:
            value: Value to validate
            field_req: Field requirements dictionary

        Returns:
            Name of first failing rule or None if all pass
        """
        from ...validator.rules import (
            check_allowed_values,
            check_date_bounds,
            check_field_pattern,
            check_field_range,
            check_field_type,
            check_length_bounds,
        )

        # Check rules in strict order
        if not check_field_type(value, field_req):
            return "type"
        if "allowed_values" in field_req and not check_allowed_values(value, field_req):
            return "allowed_values"
        if (
            ("min_length" in field_req) or ("max_length" in field_req)
        ) and not check_length_bounds(value, field_req):
            return "length_bounds"
        if "pattern" in field_req and not check_field_pattern(value, field_req):
            return "pattern"
        if (
            ("min_value" in field_req) or ("max_value" in field_req)
        ) and not check_field_range(value, field_req):
            return "numeric_range"

        date_keys = ["after_date", "before_date", "after_datetime", "before_datetime"]
        if any(k in field_req for k in date_keys) and not check_date_bounds(
            value, field_req
        ):
            return "date_bounds"

        return None

    def prepare_observed_stats(self, data: pd.DataFrame) -> dict[str, dict[str, Any]]:
        """Precompute observed statistics for training-pass relaxation.

        Args:
            data: DataFrame to analyze

        Returns:
            Dictionary mapping field names to their observed statistics
        """
        observed_stats: dict[str, dict[str, Any]] = {}

        for col in data.columns:
            series = data[col].dropna()
            if series.empty:
                observed_stats[col] = {}
                continue

            # Calculate length statistics
            try:
                lengths = series.astype(str).str.len()
                min_len = int(lengths.min()) if not lengths.empty else None
                max_len = int(lengths.max()) if not lengths.empty else None
            except Exception:
                min_len = max_len = None

            # Calculate numeric statistics
            try:
                numeric_series = pd.to_numeric(series, errors="coerce")
                if numeric_series.notna().any():
                    min_val = float(numeric_series.min())
                    max_val = float(numeric_series.max())
                else:
                    min_val = max_val = None
            except Exception:
                min_val = max_val = None

            observed_stats[col] = {
                "min_len": min_len,
                "max_len": max_len,
                "min_val": min_val,
                "max_val": max_val,
            }

        return observed_stats

    def relax_constraint_for_failure(
        self,
        col: str,
        failing_rule: str,
        field_req: dict[str, Any],
        observed_stats: dict[str, Any],
        adjustments_log: dict[str, Any],
    ) -> None:
        """Relax a failing constraint to ensure training-pass guarantee.

        Args:
            col: Column name
            failing_rule: Name of the rule that failed
            field_req: Field requirements dictionary (modified in-place)
            observed_stats: Observed statistics for the field
            adjustments_log: Log to record adjustments made
        """
        if failing_rule == "type":
            # Convert to string type and remove incompatible constraints
            if field_req.get("type") != "string":
                old_type = field_req.get("type")
                field_req["type"] = "string"

                # Remove numeric/date constraints
                removed_keys = []
                for k in [
                    "min_value",
                    "max_value",
                    "after_date",
                    "before_date",
                    "after_datetime",
                    "before_datetime",
                ]:
                    if k in field_req:
                        field_req.pop(k, None)
                        removed_keys.append(k)

                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "type",
                        "action": "coerced_to_string",
                        "reason": "training-pass failure",
                        "before": old_type,
                        "removed_constraints": removed_keys,
                    }
                )

        elif failing_rule == "allowed_values":
            # Remove allowed values constraint
            if "allowed_values" in field_req:
                old_values = field_req.pop("allowed_values", None)
                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "allowed_values",
                        "action": "removed",
                        "reason": "training-pass failure",
                        "before": old_values,
                    }
                )

        elif failing_rule == "length_bounds":
            # Widen length bounds or remove if no stats available
            stats = observed_stats or {}
            if stats.get("min_len") is not None and stats.get("max_len") is not None:
                before_min = field_req.get("min_length")
                before_max = field_req.get("max_length")

                field_req["min_length"] = min(
                    int(field_req.get("min_length", stats["min_len"])),
                    int(stats["min_len"]),
                )
                field_req["max_length"] = max(
                    int(field_req.get("max_length", stats["max_len"])),
                    int(stats["max_len"]),
                )

                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "length_bounds",
                        "action": "widened",
                        "reason": "training-pass failure",
                        "before": {"min": before_min, "max": before_max},
                        "after": {
                            "min": field_req.get("min_length"),
                            "max": field_req.get("max_length"),
                        },
                    }
                )
            else:
                # Remove length constraints if no stats
                before_min = field_req.pop("min_length", None)
                before_max = field_req.pop("max_length", None)
                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "length_bounds",
                        "action": "removed",
                        "reason": "insufficient stats",
                        "before": {"min": before_min, "max": before_max},
                    }
                )

        elif failing_rule == "pattern":
            # Remove pattern constraint
            if "pattern" in field_req:
                old_pattern = field_req.pop("pattern", None)
                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "pattern",
                        "action": "removed",
                        "reason": "training-pass failure",
                        "before": old_pattern,
                    }
                )

        elif failing_rule == "numeric_range":
            # Widen numeric bounds
            stats = observed_stats or {}
            min_val = stats.get("min_val")
            max_val = stats.get("max_val")

            if min_val is not None and max_val is not None:
                before_min = field_req.get("min_value")
                before_max = field_req.get("max_value")

                field_req["min_value"] = min(
                    float(field_req.get("min_value", min_val)), float(min_val)
                )
                field_req["max_value"] = max(
                    float(field_req.get("max_value", max_val)), float(max_val)
                )

                adjustments_log.setdefault(col, {}).setdefault(
                    "adjustments", []
                ).append(
                    {
                        "rule": "numeric_range",
                        "action": "widened",
                        "reason": "training-pass failure",
                        "before": {"min": before_min, "max": before_max},
                        "after": {
                            "min": field_req.get("min_value"),
                            "max": field_req.get("max_value"),
                        },
                    }
                )

        elif failing_rule == "date_bounds":
            # Remove date bounds
            before_after = field_req.get("after_date") or field_req.get(
                "after_datetime"
            )
            before_before = field_req.get("before_date") or field_req.get(
                "before_datetime"
            )

            for k in ["after_date", "before_date", "after_datetime", "before_datetime"]:
                field_req.pop(k, None)

            adjustments_log.setdefault(col, {}).setdefault("adjustments", []).append(
                {
                    "rule": "date_bounds",
                    "action": "removed",
                    "reason": "training-pass failure",
                    "before": {"after": before_after, "before": before_before},
                }
            )

    def convert_field_constraints_to_validation_rules(
        self, field_req: dict[str, Any], field_name: str
    ) -> list[dict[str, Any]]:
        """Convert old-style field constraints to validation_rules list with severity.

        Args:
            field_req: Field requirement dictionary with old-style constraints
            field_name: Name of the field (for error messages)

        Returns:
            List of validation rule dictionaries ready for standard generation
        """
        from ...config.severity_loader import SeverityDefaultsLoader

        severity_loader = SeverityDefaultsLoader()
        validation_rules = []

        # 1. Completeness: not_null rule (if not nullable)
        if not field_req.get("nullable", True):
            rule = self.create_validation_rule(
                name=f"{field_name} is required",
                dimension="completeness",
                severity=severity_loader.get_severity("completeness", "not_null"),
                rule_type="not_null",
                rule_expression="IS_NOT_NULL",
                error_message=f"{field_name} must not be empty",
            )
            validation_rules.append(rule)

        # 2. Validity: type rule
        if "type" in field_req:
            field_type = field_req["type"]
            rule = self.create_validation_rule(
                name=f"{field_name} type validation",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "type"),
                rule_type="type",
                rule_expression=f"IS_{field_type.upper()}",
                error_message=f"{field_name} must be of type {field_type}",
            )
            validation_rules.append(rule)

        # 3. Validity: allowed_values rule
        if "allowed_values" in field_req:
            allowed = field_req["allowed_values"]
            rule = self.create_validation_rule(
                name=f"{field_name} must be valid value",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "allowed_values"),
                rule_type="allowed_values",
                rule_expression=f"VALUE_IN({allowed})",
                error_message=f"{field_name} must be one of: {', '.join(str(v) for v in list(allowed)[0:5])}",
            )
            validation_rules.append(rule)

        # 4. Validity: numeric_bounds rule
        if "min_value" in field_req or "max_value" in field_req:
            min_val = field_req.get("min_value")
            max_val = field_req.get("max_value")
            expr_parts = []
            if min_val is not None:
                expr_parts.append(f"VALUE >= {min_val}")
            if max_val is not None:
                expr_parts.append(f"VALUE <= {max_val}")

            rule = self.create_validation_rule(
                name=f"{field_name} numeric bounds",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "numeric_bounds"),
                rule_type="numeric_bounds",
                rule_expression=" AND ".join(expr_parts),
                error_message=f"{field_name} must be between {min_val} and {max_val}",
            )
            validation_rules.append(rule)

        # 5. Validity: length_bounds rule
        if "min_length" in field_req or "max_length" in field_req:
            min_len = field_req.get("min_length")
            max_len = field_req.get("max_length")
            expr_parts = []
            if min_len is not None:
                expr_parts.append(f"LENGTH >= {min_len}")
            if max_len is not None:
                expr_parts.append(f"LENGTH <= {max_len}")

            rule = self.create_validation_rule(
                name=f"{field_name} length bounds",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "length_bounds"),
                rule_type="length_bounds",
                rule_expression=" AND ".join(expr_parts),
                error_message=f"{field_name} length must be between {min_len} and {max_len}",
            )
            validation_rules.append(rule)

        # 6. Validity: pattern rule
        if "pattern" in field_req:
            pattern = field_req["pattern"]
            rule = self.create_validation_rule(
                name=f"{field_name} pattern validation",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "pattern"),
                rule_type="pattern",
                rule_expression=f"REGEX_MATCH('{pattern}')",
                error_message=f"{field_name} must match pattern: {pattern}",
            )
            validation_rules.append(rule)

        # 7. Validity: date_bounds rule
        if any(
            k in field_req
            for k in ["after_date", "before_date", "after_datetime", "before_datetime"]
        ):
            after = field_req.get("after_date") or field_req.get("after_datetime")
            before = field_req.get("before_date") or field_req.get("before_datetime")
            expr_parts = []
            if after:
                expr_parts.append(f"DATE >= '{after}'")
            if before:
                expr_parts.append(f"DATE <= '{before}'")

            rule = self.create_validation_rule(
                name=f"{field_name} date bounds",
                dimension="validity",
                severity=severity_loader.get_severity("validity", "date_bounds"),
                rule_type="date_bounds",
                rule_expression=" AND ".join(expr_parts),
                error_message=f"{field_name} must be within date range",
            )
            validation_rules.append(rule)

        return validation_rules

    def create_validation_rule(
        self,
        name: str,
        dimension: str,
        severity,
        rule_type: str,
        rule_expression: str,
        error_message: str | None = None,
        remediation: str | None = None,
        penalty_weight: float = 1.0,
    ) -> dict[str, Any]:
        """Create a validation rule dictionary for standard generation.

        Args:
            name: Descriptive name for the rule
            dimension: Quality dimension (validity, completeness, etc.)
            severity: Severity level (Severity enum or string)
            rule_type: Type of rule (type, not_null, pattern, etc.)
            rule_expression: Validation expression/logic
            error_message: Optional error message
            remediation: Optional remediation guidance
            penalty_weight: Optional penalty weight (default 1.0)

        Returns:
            Dictionary representation of a validation rule
        """
        from ...core.severity import Severity as SeverityEnum

        # Convert Severity enum to string if needed
        if isinstance(severity, SeverityEnum):
            severity_str = severity.value
        else:
            severity_str = str(severity)

        rule = {
            "name": name,
            "dimension": dimension,
            "severity": severity_str,
            "rule_type": rule_type,
            "rule_expression": rule_expression,
        }

        if error_message:
            rule["error_message"] = error_message
        if remediation:
            rule["remediation"] = remediation
        if penalty_weight != 1.0:
            rule["penalty_weight"] = penalty_weight

        return rule
