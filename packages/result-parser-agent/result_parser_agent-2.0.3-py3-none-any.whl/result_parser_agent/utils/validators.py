"""Common validation utilities."""

import re
from pathlib import Path
from typing import Any

from ..exceptions import ValidationError


class PathValidator:
    """Validates file and directory paths."""

    @staticmethod
    def validate_input_path(input_path: str) -> Path:
        """Validate and return input path.

        Args:
            input_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            ValidationError: If path is invalid
        """
        path = Path(input_path)
        if not path.exists():
            raise ValidationError(f"Input path does not exist: {input_path}")
        return path

    @staticmethod
    def validate_output_path(output_path: str) -> Path:
        """Validate output path and ensure parent directory exists.

        Args:
            output_path: Output path to validate

        Returns:
            Validated Path object
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


class WorkloadValidator:
    """Validates workload names and configurations."""

    @staticmethod
    def validate_workload_name(workload_name: str) -> str:
        """Validate workload name format.

        Args:
            workload_name: Workload name to validate

        Returns:
            Normalized workload name

        Raises:
            ValidationError: If workload name is invalid
        """
        if not workload_name or not workload_name.strip():
            raise ValidationError("Workload name cannot be empty")

        # Normalize workload name
        normalized = workload_name.strip().lower()

        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r"^[a-z0-9_-]+$", normalized):
            raise ValidationError(
                f"Invalid workload name '{workload_name}'. "
                "Only alphanumeric characters, underscores, and hyphens are allowed."
            )

        return normalized

    @staticmethod
    def validate_metrics(metrics: list[str]) -> list[str]:
        """Validate metrics list.

        Args:
            metrics: List of metrics to validate

        Returns:
            Validated and cleaned metrics list

        Raises:
            ValidationError: If metrics are invalid
        """
        if not metrics:
            raise ValidationError("At least one metric must be specified")

        validated_metrics = []
        for metric in metrics:
            metric = metric.strip()
            if not metric:
                continue
            if metric in validated_metrics:
                raise ValidationError(f"Duplicate metric: {metric}")
            validated_metrics.append(metric)

        if not validated_metrics:
            raise ValidationError("No valid metrics provided")

        return validated_metrics


class ConfigValidator:
    """Validates configuration values."""

    @staticmethod
    def validate_workload_config(config: dict[str, Any]) -> dict[str, Any]:
        """Validate workload configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validated configuration

        Raises:
            ValidationError: If configuration is invalid
        """
        required_fields = ["workloadName", "metrics", "script"]
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Missing required field: {field}")

        # Validate workload name
        config["workloadName"] = WorkloadValidator.validate_workload_name(
            config["workloadName"]
        )

        # Validate metrics
        config["metrics"] = WorkloadValidator.validate_metrics(config["metrics"])

        # Validate script name
        script = config.get("script", "extractor.sh")
        if not script or not script.strip():
            raise ValidationError("Script name cannot be empty")
        config["script"] = script.strip()

        # Set default values
        config.setdefault(
            "description", f"Performance benchmark for {config['workloadName']}"
        )
        config.setdefault("status", "active")

        return config
