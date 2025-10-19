"""Base generator strategy interface."""

from abc import ABC, abstractmethod
from typing import Any

from chora_compose.core.models import ContentConfig


class GeneratorStrategy(ABC):
    """Abstract base class for content generation strategies."""

    @abstractmethod
    def generate(
        self, config: ContentConfig, context: dict[str, Any] | None = None
    ) -> str:
        """
        Generate content based on the provided configuration.

        Args:
            config: Content configuration containing elements and generation patterns
            context: Optional additional context data for generation

        Returns:
            Generated content as a string

        Raises:
            ValueError: If configuration is invalid or generation fails
        """
        pass

    def _extract_element_data(self, config: ContentConfig) -> dict[str, str]:
        """
        Extract element data into a dictionary for easy access.

        Args:
            config: Content configuration

        Returns:
            Dictionary mapping element names to their example_output
        """
        return {
            element.name: element.example_output or "" for element in config.elements
        }
