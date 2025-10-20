"""Configuration loader with JSON Schema validation."""

import json
from pathlib import Path
from typing import Optional, Union

import jsonschema
from pydantic import ValidationError

from .models import ArtifactConfig, ContentConfig


class ConfigValidationError(Exception):
    """Raised when config fails validation."""

    def __init__(self, errors: Union[list[dict], str]) -> None:
        """Initialize with validation errors."""
        self.errors = errors
        super().__init__(self._format_errors())

    def _format_errors(self) -> str:
        """Format errors for display."""
        if isinstance(self.errors, str):
            return self.errors

        messages = []
        for error in self.errors:
            if isinstance(error, dict):
                path = " -> ".join(str(p) for p in error.get("path", []))
                msg = error.get("message", "Unknown error")
                messages.append(f"  {path}: {msg}" if path else f"  {msg}")
            else:
                messages.append(f"  {error}")
        return "\n".join(messages)


class ConfigLoader:
    """Loads and validates Chora Compose configuration files."""

    def __init__(
        self,
        schema_dir: Optional[Path | str] = None,
        config_dir: Optional[Path | str] = None,
        *,
        config_root: Optional[Path | str] = None,
    ) -> None:
        """
        Initialize config loader.

        Args:
            schema_dir: Directory containing schema files (defaults to 'schemas/')
            config_dir: Base directory for config files (defaults to 'configs/')
            config_root: Deprecated alias for config_dir (for MCP compat)
        """
        if config_root is not None:
            if config_dir is not None:
                raise ValueError(
                    "config_root and config_dir are mutually exclusive parameters"
                )
            config_dir = config_root

        schema_path = Path(schema_dir) if schema_dir is not None else Path("schemas")
        config_path = Path(config_dir) if config_dir is not None else Path("configs")

        self.schema_dir = schema_path
        self.config_dir = config_path
        self._schema_cache: dict[str, dict] = {}

    def _load_json_file(self, path: Path) -> dict:
        """
        Load JSON file from path.

        Args:
            path: Path to JSON file

        Returns:
            Parsed JSON as dict

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]

    def _get_schema(self, schema_type: str, version: str = "3.1") -> dict:
        """
        Load JSON Schema for validation.

        Args:
            schema_type: Type of schema ('content' or 'artifact')
            version: Schema version (default: '3.1')

        Returns:
            JSON Schema as dict

        Raises:
            FileNotFoundError: If schema file not found
        """
        cache_key = f"{schema_type}-{version}"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        schema_path = self.schema_dir / schema_type / f"v{version}" / "schema.json"
        schema = self._load_json_file(schema_path)
        self._schema_cache[cache_key] = schema
        return schema

    def _validate_with_schema(
        self, config_data: dict, schema_type: str, version: str
    ) -> None:
        """
        Validate config data against JSON Schema.

        Args:
            config_data: Config data to validate
            schema_type: Type of schema ('content' or 'artifact')
            version: Schema version

        Raises:
            ConfigValidationError: If validation fails (includes suggested fixes)
        """
        try:
            schema = self._get_schema(schema_type, version)
            # Create validator to collect all errors
            validator = jsonschema.Draft202012Validator(schema)
            validation_errors = list(validator.iter_errors(config_data))

            if validation_errors:
                # Collect all validation errors
                errors = []
                for error in validation_errors:
                    error_dict = {
                        "path": list(error.path),
                        "message": error.message,
                    }
                    errors.append(error_dict)

                raise ConfigValidationError(errors)

        except FileNotFoundError as e:
            raise ConfigValidationError(f"Schema not found: {e}") from e

    def load_content_config(
        self,
        config_id: str,
        version: Optional[str] = None,
        config_path: Optional[Path] = None,
    ) -> ContentConfig:
        """
        Load and validate a content configuration.

        Args:
            config_id: ID of the content config to load
            version: Optional specific version to load
            config_path: Optional direct path to config file (overrides config_id)

        Returns:
            Validated ContentConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ConfigValidationError: If validation fails
        """
        # Determine config file path
        if config_path:
            path = config_path
        else:
            # Default path: configs/content/{config_id}/{config_id}-content.json
            path = self.config_dir / "content" / config_id / f"{config_id}-content.json"

        # Load config data
        config_data = self._load_json_file(path)

        # Extract schema version from config
        schema_ref = config_data.get("schemaRef", {})
        schema_version = schema_ref.get("version", "3.1")

        # Validate against JSON Schema
        self._validate_with_schema(config_data, "content", schema_version)

        # Parse with Pydantic for additional validation and type safety
        try:
            return ContentConfig.model_validate(config_data)  # type: ignore[no-any-return]
        except ValidationError as e:
            errors = [
                {"path": error["loc"], "message": error["msg"]} for error in e.errors()
            ]
            raise ConfigValidationError(errors) from e

    def load_artifact_config(
        self,
        config_id: str,
        version: Optional[str] = None,
        config_path: Optional[Path] = None,
    ) -> ArtifactConfig:
        """
        Load and validate an artifact configuration.

        Args:
            config_id: ID of the artifact config to load
            version: Optional specific version to load
            config_path: Optional direct path to config file (overrides config_id)

        Returns:
            Validated ArtifactConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ConfigValidationError: If validation fails
        """
        # Determine config file path
        if config_path:
            path = config_path
        else:
            # Default path: configs/artifacts/{config_id}-artifact.json
            path = self.config_dir / "artifacts" / f"{config_id}-artifact.json"

        # Load config data
        config_data = self._load_json_file(path)

        # Extract schema version from config
        schema_ref = config_data.get("schemaRef", {})
        schema_version = schema_ref.get("version", "3.1")

        # Validate against JSON Schema
        self._validate_with_schema(config_data, "artifact", schema_version)

        # Parse with Pydantic for additional validation and type safety
        try:
            return ArtifactConfig.model_validate(config_data)  # type: ignore[no-any-return]
        except ValidationError as e:
            errors = [
                {"path": error["loc"], "message": error["msg"]} for error in e.errors()
            ]
            raise ConfigValidationError(errors) from e

    def load_config(self, config_path: Path) -> Union[ContentConfig, ArtifactConfig]:
        """
        Load any config type by auto-detecting from the 'type' field.

        Args:
            config_path: Path to config file

        Returns:
            ContentConfig or ArtifactConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ConfigValidationError: If validation fails or type unknown
        """
        config_data = self._load_json_file(config_path)
        config_type = config_data.get("type")

        if config_type == "content":
            return self.load_content_config(config_id="", config_path=config_path)
        elif config_type == "artifact":
            return self.load_artifact_config(config_id="", config_path=config_path)
        else:
            raise ConfigValidationError(
                f"Unknown config type: {config_type}. Must be 'content' or 'artifact'"
            )
