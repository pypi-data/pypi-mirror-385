"""Demonstration generator using example_output from elements."""

import re
import time
from typing import Any

from chora_compose.core.models import ContentConfig
from chora_compose.models import UpstreamDependencies
from chora_compose.telemetry import ContentGeneratedEvent, emit_event

from .base import GeneratorStrategy


class DemonstrationGenerator(GeneratorStrategy):
    """
    Generator that uses example_output from elements.

    This is the simplest generation type - it extracts the example_output
    field from elements and substitutes them into a template using simple
    {{variable}} placeholder replacement.
    """

    def __init__(self) -> None:
        """Attach generator metadata for discovery tooling."""
        self.version = "1.0.0"
        self.description = "Uses example_output values to assemble quick demos."
        self.capabilities = ["basic_generation", "variables"]
        self.upstream_dependencies = UpstreamDependencies(
            services=[],  # No external services
            credentials_required=[],  # No credentials needed
            concurrency_safe=True,  # Pure string manipulation, safe for concurrent use
            stability="stable",
        )

    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate content by extracting example_output and substituting into template.

        Args:
            config: Content configuration with elements containing example_output
            context: Optional additional context (not used in demonstration mode)

        Returns:
            Generated content with all variables substituted

        Raises:
            ValueError: If no demonstration pattern found or required elements missing
        """
        start_time = time.time()
        status = "success"
        error_message = None

        try:
            # Find the demonstration generation pattern
            if not config.generation or not config.generation.patterns:
                raise ValueError(
                    f"Config '{config.id}' has no generation patterns defined"
                )

            demo_pattern = None
            for pattern in config.generation.patterns:
                if pattern.type == "demonstration":
                    demo_pattern = pattern
                    break

            if not demo_pattern:
                raise ValueError(
                    f"Config '{config.id}' has no demonstration generation pattern"
                )

            # Extract element data
            element_data = self._extract_element_data(config)

            # Build variables dictionary from pattern
            variables = {}
            for var in demo_pattern.variables:
                value = self._resolve_variable_source(var.source, element_data, config)
                if value is None and var.default:
                    value = var.default
                if value is None:
                    raise ValueError(
                        f"Cannot resolve variable '{var.name}' "
                        f"from source '{var.source}'"
                    )
                variables[var.name] = value

            # Substitute template
            template = demo_pattern.template or ""
            result = self._substitute_template(template, variables)

            return result
        except Exception as e:
            status = "error"
            error_message = str(e)
            raise
        finally:
            # Emit telemetry event
            duration_ms = int((time.time() - start_time) * 1000)
            emit_event(
                ContentGeneratedEvent(
                    content_config_id=config.id,
                    generator_type="demonstration",
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            )

    def _resolve_variable_source(
        self, source: str, element_data: dict[str, str], config: ContentConfig
    ) -> str | None:
        """
        Resolve a variable source path to actual data.

        Supports sources like:
        - "elements.intro.example_output" -> element_data["intro"]
        - "elements.0.example_output" -> config.elements[0].example_output

        Args:
            source: Source path string
            element_data: Pre-extracted element data
            config: Full content config for indexed access

        Returns:
            Resolved value or None if not found
        """
        # Handle elements.{name}.example_output
        if source.startswith("elements."):
            parts = source.split(".")
            if len(parts) < 2:
                return None

            identifier = parts[1]

            # Try by name first
            if identifier in element_data:
                return element_data[identifier]

            # Try by index
            try:
                index = int(identifier)
                if 0 <= index < len(config.elements):
                    return config.elements[index].example_output or ""
            except ValueError:
                pass

        return None

    def _substitute_template(self, template: str, variables: dict[str, str]) -> str:
        """
        Substitute {{variable}} placeholders in template with actual values.

        Args:
            template: Template string with {{variable}} placeholders
            variables: Dictionary mapping variable names to values

        Returns:
            Template with all variables substituted
        """
        result = template

        # Replace each variable
        for var_name, var_value in variables.items():
            # Use regex to find {{var_name}} with optional whitespace
            pattern = r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}"
            result = re.sub(pattern, var_value, result)

        # Unescape newlines in template (JSON escapes them)
        result = result.replace("\\n", "\n")
        result = result.replace("\\t", "\t")

        return result
