"""Jinja2-based content generator."""

import json
import time
from pathlib import Path
from typing import Any

from chora_compose.core.models import ContentConfig
from chora_compose.generators.base import GeneratorStrategy
from chora_compose.models import UpstreamDependencies
from chora_compose.telemetry import ContentGeneratedEvent, emit_event
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, UndefinedError


class GenerationError(Exception):
    """Raised when Jinja2 generation fails."""

    pass


class Jinja2Generator(GeneratorStrategy):
    """
    Generates content using Jinja2 templates.

    This generator loads Jinja2 templates and renders them with context data.
    Supports template inheritance, macros, filters, and all Jinja2 features.

    The generator uses context from content config's
    generation.patterns[].generation_config.context
    or from explicitly provided context parameter.
    """

    def __init__(self, template_dir: Path | None = None, **jinja_options: Any) -> None:
        """
        Initialize the Jinja2 generator.

        Args:
            template_dir: Directory containing Jinja2 template files.
                         If None, uses current working directory.
            **jinja_options: Additional options passed to jinja2.Environment().
        """
        self.template_dir = template_dir or Path.cwd()
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)), **jinja_options
        )
        self.version = "0.9.0"
        self.description = (
            "Full Jinja2 template engine with conditionals, loops, and filters."
        )
        self.capabilities = ["template", "conditionals", "loops", "filters"]
        self.upstream_dependencies = UpstreamDependencies(
            services=[],  # Local template rendering only
            credentials_required=[],  # No credentials needed
            concurrency_safe=True,  # File system reads, safe for concurrent use
            stability="stable",
        )

    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate content by rendering a Jinja2 template with context data.

        Args:
            config: Content configuration containing generation pattern
            context: Additional context to merge with config's context

        Returns:
            Generated content from rendered template

        Raises:
            GenerationError: If generation fails
        """
        start_time = time.time()
        status = "success"
        error_message = None

        try:
            # Find Jinja2 pattern
            if not config.generation or not config.generation.patterns:
                raise GenerationError(
                    f"No generation patterns found in config '{config.id}'"
                )

            jinja2_pattern = None
            for pattern in config.generation.patterns:
                if pattern.type == "jinja2":
                    jinja2_pattern = pattern
                    break

            if not jinja2_pattern:
                raise GenerationError(
                    f"No jinja2 generation pattern found in config '{config.id}'"
                )

            # Get template name
            template_name = jinja2_pattern.template
            if not template_name:
                raise GenerationError(
                    f"No template specified in jinja2 pattern '{jinja2_pattern.id}'"
                )

            # Merge contexts: config context + runtime context
            merged_context = {}

            # Get context from generation_config if present
            if jinja2_pattern.generation_config:
                pattern_context = jinja2_pattern.generation_config.get("context", {})
                merged_context.update(pattern_context)

            # Override with runtime context
            if context:
                merged_context.update(context)

            # Resolve context sources (e.g., file loading)
            resolved_context = self._resolve_context_sources(merged_context)

            # Load and render template
            template = self.env.get_template(template_name)
            output = template.render(**resolved_context)

            return str(output)

        except TemplateNotFound as e:
            status = "error"
            error_message = f"Template not found: {e.name}"
            raise GenerationError(
                f"Template not found: {e.name}. Template directory: {self.template_dir}"
            ) from e

        except UndefinedError as e:
            status = "error"
            error_message = f"Undefined variable: {str(e)}"
            raise GenerationError(f"Undefined variable in template: {str(e)}") from e

        except Exception as e:
            status = "error"
            error_message = f"{type(e).__name__}: {str(e)}"
            raise GenerationError(
                f"Template rendering failed: {type(e).__name__}: {str(e)}"
            ) from e
        finally:
            # Emit telemetry event
            duration_ms = int((time.time() - start_time) * 1000)
            emit_event(
                ContentGeneratedEvent(
                    content_config_id=config.id,
                    generator_type="jinja2",
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            )

    def register_filter(self, name: str, filter_func: Any) -> None:
        """
        Register a custom Jinja2 filter.

        Args:
            name: Name of the filter
            filter_func: Function implementing the filter
        """
        self.env.filters[name] = filter_func

    def register_global(self, name: str, value: Any) -> None:
        """
        Register a global variable or function available in all templates.

        Args:
            name: Name of the global
            value: Value of the global (can be any Python object)
        """
        self.env.globals[name] = value

    def _resolve_context_sources(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Resolve context values that reference external sources.

        Args:
            context: Context dictionary potentially containing source references

        Returns:
            Context with all sources resolved to actual values
        """
        resolved = {}

        for key, value in context.items():
            # Check if value is a dict with "source" key
            if isinstance(value, dict) and "source" in value:
                if value["source"] == "file":
                    # Load file content
                    file_path = Path(value["path"])
                    try:
                        if file_path.suffix == ".json":
                            with open(file_path) as f:
                                resolved[key] = json.load(f)
                        else:
                            resolved[key] = file_path.read_text()
                    except Exception as e:
                        raise GenerationError(
                            f"Failed to load file source '{file_path}': {e}"
                        ) from e
                elif value["source"] == "config":
                    # TODO: Load config - for future implementation
                    raise GenerationError(
                        f"Config source loading not yet implemented for '{key}'"
                    )
                else:
                    # Unknown source type, pass through
                    resolved[key] = value
            else:
                # Not a source reference, pass through
                resolved[key] = value

        return resolved
