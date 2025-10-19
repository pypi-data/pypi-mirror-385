"""Template fill generator using simple {{variable}} substitution."""

import re
import time
from typing import Any

from chora_compose.core.models import ContentConfig
from chora_compose.generators.base import GeneratorStrategy
from chora_compose.models import UpstreamDependencies
from chora_compose.telemetry import ContentGeneratedEvent, emit_event


class TemplateFillError(Exception):
    """Raised when template filling fails."""

    pass


class TemplateFillGenerator(GeneratorStrategy):
    """
    Simple template generator using {{variable}} substitution.

    This generator provides lightweight template filling without the complexity
    of Jinja2. It's ideal for simple substitutions where template inheritance,
    filters, and other advanced features aren't needed.

    Key differences from other generators:
    - DemonstrationGenerator: Extracts from elements.*.example_output
    - TemplateFillGenerator: Uses variables from context directly
    - Jinja2Generator: Full template engine with inheritance, filters, macros

    The generator:
    1. Finds the template_fill pattern in config.generation.patterns
    2. Extracts template string
    3. Substitutes {{variable}} placeholders with context values
    4. Handles undefined variables based on configuration
    """

    def __init__(
        self,
        undefined_behavior: str = "error",
        escape_sequences: bool = True,
    ) -> None:
        """
        Initialize the template fill generator.

        Args:
            undefined_behavior: How to handle undefined variables:
                - "error": Raise TemplateFillError (default)
                - "keep": Keep {{variable}} placeholder as-is
                - "empty": Replace with empty string
            escape_sequences: If True, process escape sequences (\\n, \\t, etc.)
        """
        if undefined_behavior not in ("error", "keep", "empty"):
            raise ValueError(
                f"Invalid undefined_behavior: {undefined_behavior}. "
                "Must be 'error', 'keep', or 'empty'."
            )

        self.undefined_behavior = undefined_behavior
        self.escape_sequences = escape_sequences
        self.version = "1.0.0"
        self.description = (
            "Lightweight {{variable}} substitution for markdown and text."
        )
        self.capabilities = ["template", "simple_substitution"]
        self.upstream_dependencies = UpstreamDependencies(
            services=[],  # Local string substitution only
            credentials_required=[],  # No credentials needed
            concurrency_safe=True,  # Pure string manipulation, safe for concurrent use
            stability="stable",
        )

    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate content by filling template with context values.

        Args:
            config: Content configuration containing template_fill pattern
            context: Dictionary of variable name → value mappings

        Returns:
            Template with all variables substituted

        Raises:
            TemplateFillError: If pattern not found or variables undefined
        """
        start_time = time.time()
        status = "success"
        error_message = None

        try:
            # Find template_fill pattern
            if not config.generation or not config.generation.patterns:
                raise TemplateFillError(
                    f"Config '{config.id}' has no generation patterns defined"
                )

            template_pattern = None
            for pattern in config.generation.patterns:
                if pattern.type == "template_fill":
                    template_pattern = pattern
                    break

            if not template_pattern:
                raise TemplateFillError(
                    f"Config '{config.id}' has no template_fill generation pattern"
                )

            # Get template
            template = template_pattern.template or ""

            # Merge context: generation_config context + runtime context
            merged_context = {}

            # Get context from generation_config if present
            if template_pattern.generation_config:
                pattern_context = template_pattern.generation_config.get("context", {})
                merged_context.update(pattern_context)

            # Override with runtime context
            if context:
                merged_context.update(context)

            # Get undefined behavior from config (overrides instance setting)
            undefined_behavior = self.undefined_behavior
            if template_pattern.generation_config:
                undefined_behavior = template_pattern.generation_config.get(
                    "undefined_behavior", undefined_behavior
                )

            # Fill template
            result = self._fill_template(template, merged_context, undefined_behavior)

            # Process escape sequences if enabled
            if self.escape_sequences:
                result = self._process_escape_sequences(result)

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
                    generator_type="template_fill",
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            )

    def _fill_template(
        self, template: str, context: dict[str, Any], undefined_behavior: str
    ) -> str:
        """
        Fill template with context values.

        Args:
            template: Template string with {{variable}} placeholders
            context: Variable values
            undefined_behavior: How to handle undefined variables

        Returns:
            Filled template

        Raises:
            TemplateFillError: If undefined_behavior="error" and variable not found
        """
        # Find all {{variable}} patterns
        pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\}\}"

        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)

            # Support nested dict access via dot notation (e.g., {{user.name}})
            value = self._get_nested_value(context, var_name)

            if value is None:
                if undefined_behavior == "error":
                    raise TemplateFillError(
                        f"Undefined variable: '{var_name}'. "
                        f"Available variables: {', '.join(context.keys())}"
                    )
                elif undefined_behavior == "keep":
                    return match.group(0)  # Keep {{var_name}}
                else:  # empty
                    return ""

            return str(value)

        return re.sub(pattern, replace_var, template)

    def _get_nested_value(self, data: dict[str, Any], path: str) -> Any:
        """
        Get value from nested dict using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "user.profile.name")

        Returns:
            Value at path, or None if not found
        """
        parts = path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _process_escape_sequences(self, text: str) -> str:
        """
        Process common escape sequences in text.

        Args:
            text: Text potentially containing escape sequences

        Returns:
            Text with escape sequences processed
        """
        # Process common escape sequences
        replacements = {
            "\\n": "\n",
            "\\t": "\t",
            "\\r": "\r",
            "\\\\'": "'",
            '\\\\"': '"',
            "\\\\": "\\",
        }

        result = text
        for escape, replacement in replacements.items():
            result = result.replace(escape, replacement)

        return result
