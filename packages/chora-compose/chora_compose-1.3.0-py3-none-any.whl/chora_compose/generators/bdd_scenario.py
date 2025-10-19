"""BDD Scenario generator for creating Gherkin feature files."""

import re
import time
from typing import Any

from chora_compose.core.models import ContentConfig
from chora_compose.generators.base import GeneratorStrategy
from chora_compose.models import UpstreamDependencies
from chora_compose.telemetry import ContentGeneratedEvent, emit_event


class BDDScenarioError(Exception):
    """Raised when BDD scenario generation fails."""

    pass


class BDDScenarioGenerator(GeneratorStrategy):
    """
    Generate Gherkin feature files from structured configuration.

    This generator creates BDD (Behavior-Driven Development) test scenarios
    in Gherkin format, supporting features, scenarios, backgrounds, tags,
    and scenario outlines.

    Gherkin syntax:
        Feature: Feature title
          Feature description

        Background:
          Given setup step

        @tag1 @tag2
        Scenario: Scenario title
          Given precondition
          When action
          Then expected result

    Example config:
        {
            "type": "bdd_scenario_assembly",
            "generation_config": {
                "feature": {
                    "title": "User Authentication",
                    "description": "As a user...",
                    "tags": ["@smoke", "@auth"]
                },
                "background": [
                    "Given the application is running"
                ],
                "scenarios": [
                    {
                        "title": "Successful login",
                        "tags": ["@happy-path"],
                        "steps": [
                            "Given I am on the login page",
                            "When I enter valid credentials",
                            "Then I should see the dashboard"
                        ]
                    }
                ]
            }
        }
    """

    # Valid Gherkin step keywords
    STEP_KEYWORDS = {"Given", "When", "Then", "And", "But", "*"}

    def __init__(
        self,
        indent_spaces: int = 2,
        validate_gherkin: bool = True,
    ) -> None:
        """
        Initialize the BDD scenario generator.

        Args:
            indent_spaces: Number of spaces for indentation (default: 2)
            validate_gherkin: Validate Gherkin syntax (default: True)
        """
        self.indent_spaces = indent_spaces
        self.validate_gherkin = validate_gherkin
        self.version = "0.8.0"
        self.description = "Assembles BDD scenarios into valid Gherkin feature files."
        self.capabilities = ["testing", "gherkin"]
        self.upstream_dependencies = UpstreamDependencies(
            services=[],  # Local Gherkin generation only
            credentials_required=[],  # No credentials needed
            concurrency_safe=True,  # Pure string formatting, safe for concurrent use
            stability="stable",
        )

    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate Gherkin feature file from configuration.

        Args:
            config: Content configuration with bdd_scenario_assembly pattern
            context: Runtime context for variable substitution

        Returns:
            Generated Gherkin feature file as string

        Raises:
            BDDScenarioError: If generation fails or validation errors
        """
        start_time = time.time()
        status = "success"
        error_message = None

        try:
            # Find bdd_scenario_assembly pattern
            if not config.generation or not config.generation.patterns:
                raise BDDScenarioError(
                    f"Config '{config.id}' has no generation patterns defined"
                )

            bdd_pattern = None
            for pattern in config.generation.patterns:
                if pattern.type == "bdd_scenario_assembly":
                    bdd_pattern = pattern
                    break

            if not bdd_pattern:
                raise BDDScenarioError(
                    f"Config '{config.id}' has no bdd_scenario_assembly pattern"
                )

            # Extract configuration
            gen_config = bdd_pattern.generation_config or {}

            feature_config = gen_config.get("feature")
            if not feature_config:
                raise BDDScenarioError("No 'feature' configuration provided")

            background_steps = gen_config.get("background", [])
            scenarios = gen_config.get("scenarios", [])
            scenario_outlines = gen_config.get("scenario_outlines", [])

            # Merge context
            merged_context = {}
            if gen_config.get("context"):
                merged_context.update(gen_config["context"])
            if context:
                merged_context.update(context)

            # Build Gherkin content
            parts = []

            # Feature section
            feature_section = self._build_feature(feature_config, merged_context)
            parts.append(feature_section)

            # Background section
            if background_steps:
                background_section = self._build_background(
                    background_steps, merged_context
                )
                parts.append(background_section)

            # Scenarios
            for scenario in scenarios:
                scenario_section = self._build_scenario(scenario, merged_context)
                parts.append(scenario_section)

            # Scenario Outlines
            for outline in scenario_outlines:
                outline_section = self._build_scenario_outline(outline, merged_context)
                parts.append(outline_section)

            # Join all parts
            result = "\n\n".join(parts)

            # Validate if enabled
            if self.validate_gherkin:
                self._validate_gherkin_syntax(result)

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
                    generator_type="bdd_scenario",
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_message,
                )
            )

    def _build_feature(
        self, feature_config: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """
        Build feature section.

        Args:
            feature_config: Feature configuration dict
            context: Variable context

        Returns:
            Feature section as string
        """
        title = self._substitute_variables(
            feature_config.get("title", "Untitled Feature"), context
        )
        description = feature_config.get("description", "")
        tags = feature_config.get("tags", [])

        parts = []

        # Tags
        if tags:
            formatted_tags = self._format_tags(tags)
            parts.append(formatted_tags)

        # Feature line
        parts.append(f"Feature: {title}")

        # Description (indented)
        if description:
            desc_lines = description.strip().split("\n")
            for line in desc_lines:
                if line.strip():
                    parts.append(self._indent(line.strip(), 1))
                else:
                    parts.append("")

        return "\n".join(parts)

    def _build_background(self, steps: list[str], context: dict[str, Any]) -> str:
        """
        Build background section.

        Args:
            steps: List of step strings
            context: Variable context

        Returns:
            Background section as string
        """
        parts = ["Background:"]

        for step in steps:
            step_text = self._substitute_variables(step, context)
            self._validate_step(step_text)
            parts.append(self._indent(step_text, 1))

        return "\n".join(parts)

    def _build_scenario(
        self, scenario_config: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """
        Build scenario section.

        Args:
            scenario_config: Scenario configuration dict
            context: Variable context

        Returns:
            Scenario section as string

        Raises:
            BDDScenarioError: If scenario missing required fields
        """
        title = scenario_config.get("title")
        if not title:
            raise BDDScenarioError("Scenario missing 'title'")

        steps = scenario_config.get("steps", [])
        if not steps:
            raise BDDScenarioError(f"Scenario '{title}' has no steps")

        tags = scenario_config.get("tags", [])

        parts = []

        # Tags
        if tags:
            formatted_tags = self._format_tags(tags)
            parts.append(formatted_tags)

        # Scenario line
        title_text = self._substitute_variables(title, context)
        parts.append(f"Scenario: {title_text}")

        # Steps
        for step in steps:
            step_text = self._substitute_variables(step, context)
            self._validate_step(step_text)
            parts.append(self._indent(step_text, 1))

        return "\n".join(parts)

    def _build_scenario_outline(
        self, outline_config: dict[str, Any], context: dict[str, Any]
    ) -> str:
        """
        Build scenario outline section.

        Args:
            outline_config: Scenario outline configuration dict
            context: Variable context

        Returns:
            Scenario outline section as string

        Raises:
            BDDScenarioError: If outline missing required fields
        """
        title = outline_config.get("title")
        if not title:
            raise BDDScenarioError("Scenario Outline missing 'title'")

        steps = outline_config.get("steps", [])
        if not steps:
            raise BDDScenarioError(f"Scenario Outline '{title}' has no steps")

        examples = outline_config.get("examples")
        if not examples:
            raise BDDScenarioError(f"Scenario Outline '{title}' has no examples")

        tags = outline_config.get("tags", [])

        parts = []

        # Tags
        if tags:
            formatted_tags = self._format_tags(tags)
            parts.append(formatted_tags)

        # Scenario Outline line
        title_text = self._substitute_variables(title, context)
        parts.append(f"Scenario Outline: {title_text}")

        # Steps
        for step in steps:
            step_text = self._substitute_variables(step, context)
            # Don't validate outline steps (they contain <placeholders>)
            parts.append(self._indent(step_text, 1))

        # Examples section
        parts.append("")
        parts.append(self._indent("Examples:", 1))

        # Examples table
        headers = examples.get("headers", [])
        rows = examples.get("rows", [])

        if headers:
            # Header row
            header_row = "| " + " | ".join(headers) + " |"
            parts.append(self._indent(header_row, 2))

            # Data rows
            for row in rows:
                data_row = "| " + " | ".join(str(cell) for cell in row) + " |"
                parts.append(self._indent(data_row, 2))

        return "\n".join(parts)

    def _format_tags(self, tags: list[str]) -> str:
        """
        Format tags for Gherkin.

        Args:
            tags: List of tag strings

        Returns:
            Formatted tag string

        Raises:
            BDDScenarioError: If tag format invalid
        """
        formatted = []
        for tag in tags:
            # Ensure tag starts with @
            if not tag.startswith("@"):
                tag = f"@{tag}"

            # Validate tag format
            if not re.match(r"^@[a-zA-Z][a-zA-Z0-9_-]*$", tag):
                raise BDDScenarioError(
                    f"Invalid tag format: '{tag}'. "
                    "Tags must start with @ followed by alphanumeric/underscore/hyphen"
                )

            formatted.append(tag)

        return " ".join(formatted)

    def _validate_step(self, step: str) -> None:
        """
        Validate step syntax.

        Args:
            step: Step string

        Raises:
            BDDScenarioError: If step format invalid
        """
        if not self.validate_gherkin:
            return

        # Check if step starts with valid keyword
        parts = step.split(None, 1)
        if not parts:
            raise BDDScenarioError("Empty step")

        keyword = parts[0]
        if keyword not in self.STEP_KEYWORDS:
            raise BDDScenarioError(
                f"Invalid step keyword: '{keyword}'. "
                f"Must be one of: {', '.join(self.STEP_KEYWORDS)}"
            )

    def _validate_gherkin_syntax(self, content: str) -> None:
        """
        Validate basic Gherkin syntax.

        Args:
            content: Generated Gherkin content

        Raises:
            BDDScenarioError: If syntax invalid
        """
        if not self.validate_gherkin:
            return

        # Check for Feature keyword
        if not re.search(r"^Feature:", content, re.MULTILINE):
            raise BDDScenarioError("Gherkin must contain 'Feature:' keyword")

        # Check for at least one Scenario
        if not re.search(r"^(Scenario|Scenario Outline):", content, re.MULTILINE):
            raise BDDScenarioError(
                "Gherkin must contain at least one 'Scenario:' or 'Scenario Outline:'"
            )

    def _substitute_variables(self, text: str, context: dict[str, Any]) -> str:
        """
        Substitute {{variable}} placeholders in text.

        Args:
            text: Text with placeholders
            context: Variable values

        Returns:
            Text with variables substituted
        """
        result = text
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def _indent(self, text: str, level: int) -> str:
        """
        Indent text by specified level.

        Args:
            text: Text to indent
            level: Indentation level

        Returns:
            Indented text
        """
        spaces = " " * (self.indent_spaces * level)
        return f"{spaces}{text}"
