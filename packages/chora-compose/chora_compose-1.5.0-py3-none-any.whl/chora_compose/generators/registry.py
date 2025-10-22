"""Generator Registry for dynamic generator registration and plugin discovery."""

import importlib.util
import inspect
import threading
from pathlib import Path
from typing import Optional

from chora_compose.generators.base import GeneratorStrategy


class RegistryError(Exception):
    """Raised when generator registration fails."""

    pass


class GeneratorRegistry:
    """
    Singleton registry for content generators with plugin support.

    Supports three-tier registration:
    1. Built-in generators (shipped with package)
    2. Auto-discovered plugins (from directories)
    3. Runtime-registered (programmatic API)

    Thread-safe singleton implementation.
    """

    _instance: Optional["GeneratorRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "GeneratorRegistry":
        """Create or return singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry (only once)."""
        if self._initialized:
            return

        self._generators: dict[str, GeneratorStrategy] = {}
        self._plugin_cache: dict[str, float] = {}  # path -> mtime for invalidation
        self._initialized = True

        # Register built-in generators
        self._register_builtin_generators()

        # Auto-discover plugins
        self.discover_plugins()

    def _register_builtin_generators(self) -> None:
        """Register built-in generators shipped with the package."""
        # Import here to avoid circular imports
        from chora_compose.generators.bdd_scenario import BDDScenarioGenerator
        from chora_compose.generators.demonstration import DemonstrationGenerator
        from chora_compose.generators.jinja2 import Jinja2Generator
        from chora_compose.generators.template_fill import TemplateFillGenerator

        self.register("demonstration", DemonstrationGenerator())
        self.register("jinja2", Jinja2Generator())
        self.register("template_fill", TemplateFillGenerator())
        self.register("bdd_scenario_assembly", BDDScenarioGenerator())

        # Register code_generation only if anthropic is available
        try:
            from chora_compose.generators.code_generation import (
                CodeGenerationGenerator,
            )

            # Only register if API key is available
            try:
                self.register("code_generation", CodeGenerationGenerator())
            except Exception as e:
                # Log why code_generation failed to register
                import sys

                print(
                    f"⚠️  code_generation generator not registered: {e}",
                    file=sys.stderr,
                )
        except ImportError:
            # anthropic package not installed, skip silently
            pass

    def register(
        self, generator_type: str, generator: GeneratorStrategy, override: bool = False
    ) -> None:
        """
        Register a generator for a specific type.

        Args:
            generator_type: Type identifier (e.g., "jinja2", "custom-template")
            generator: Generator instance implementing GeneratorStrategy
            override: If True, allow overriding existing generators

        Raises:
            RegistryError: If type already registered and override=False
            RegistryError: If generator doesn't implement GeneratorStrategy
        """
        # Validate generator type pattern
        if not self._is_valid_type(generator_type):
            raise RegistryError(
                f"Invalid generator type '{generator_type}'. "
                "Must start with lowercase letter and contain only "
                "lowercase letters, numbers, hyphens, and underscores."
            )

        # Validate generator implements interface
        if not isinstance(generator, GeneratorStrategy):
            raise RegistryError(
                f"Generator must implement GeneratorStrategy interface. "
                f"Got: {type(generator).__name__}"
            )

        # Check for conflicts
        if generator_type in self._generators and not override:
            raise RegistryError(
                f"Generator type '{generator_type}' already registered. "
                "Use override=True to replace."
            )

        self._generators[generator_type] = generator

    def get(self, generator_type: str) -> GeneratorStrategy:
        """
        Retrieve a generator by type.

        Args:
            generator_type: Type identifier

        Returns:
            Generator instance

        Raises:
            RegistryError: If generator type not found
        """
        if generator_type not in self._generators:
            raise RegistryError(
                f"Generator type '{generator_type}' not found. "
                f"Available types: {', '.join(self.list_types())}"
            )

        return self._generators[generator_type]

    def discover_plugins(self, force_reload: bool = False) -> list[str]:
        """
        Auto-discover generator plugins from standard directories.

        Scans:
        - ~/.chora-compose/generators/
        - .chora-compose/generators/ (project-local)

        Plugin files must:
        - Match pattern: *_generator.py
        - Contain a class inheriting from GeneratorStrategy
        - Expose generator_type and generator_class attributes

        Args:
            force_reload: If True, reload even if files haven't changed

        Returns:
            List of discovered generator type names

        Raises:
            RegistryError: If plugin loading fails
        """
        discovered = []

        plugin_dirs = [
            Path.home() / ".chora-compose" / "generators",
            Path.cwd() / ".chora-compose" / "generators",
        ]

        for plugin_dir in plugin_dirs:
            if not plugin_dir.exists():
                continue

            for plugin_file in plugin_dir.glob("*_generator.py"):
                # Check if file has been modified
                mtime = plugin_file.stat().st_mtime
                cache_key = str(plugin_file)

                if not force_reload and cache_key in self._plugin_cache:
                    if self._plugin_cache[cache_key] == mtime:
                        continue  # Skip unchanged files

                # Load plugin
                try:
                    generator_type = self._load_plugin(plugin_file)
                    self._plugin_cache[cache_key] = mtime
                    discovered.append(generator_type)
                except Exception as e:
                    # Log warning but don't fail - allow other plugins to load
                    print(
                        f"Warning: Failed to load plugin {plugin_file.name}: {e}",
                    )

        return discovered

    def _load_plugin(self, plugin_file: Path) -> str:
        """
        Load a single plugin module.

        Args:
            plugin_file: Path to plugin Python file

        Returns:
            Generator type name

        Raises:
            RegistryError: If plugin is invalid
        """
        # Import the module
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        if spec is None or spec.loader is None:
            raise RegistryError(f"Cannot load plugin spec from {plugin_file}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find GeneratorStrategy subclass
        generator_class = None
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, GeneratorStrategy)
                and obj is not GeneratorStrategy
                and obj.__module__ == module.__name__
            ):
                generator_class = obj
                break

        if generator_class is None:
            raise RegistryError(
                f"Plugin {plugin_file.name} does not contain "
                f"a GeneratorStrategy subclass"
            )

        # Get generator type from module or class
        if hasattr(module, "GENERATOR_TYPE"):
            generator_type = module.GENERATOR_TYPE
        elif hasattr(generator_class, "GENERATOR_TYPE"):
            generator_type = generator_class.GENERATOR_TYPE
        else:
            # Default: derive from filename (remove _generator.py suffix)
            generator_type = plugin_file.stem.replace("_generator", "")

        # Instantiate and register
        try:
            generator_instance = generator_class()
            self.register(generator_type, generator_instance, override=True)
            return generator_type
        except Exception as e:
            raise RegistryError(
                f"Failed to instantiate generator from {plugin_file.name}: {e}"
            ) from e

    def list_types(self) -> list[str]:
        """
        List all registered generator types.

        Returns:
            Sorted list of generator type names
        """
        return sorted(self._generators.keys())

    def unregister(self, generator_type: str) -> None:
        """
        Remove a generator from the registry.

        Args:
            generator_type: Type identifier to remove

        Raises:
            RegistryError: If type not found
        """
        if generator_type not in self._generators:
            raise RegistryError(f"Generator type '{generator_type}' not registered")

        del self._generators[generator_type]

    def _is_valid_type(self, generator_type: str) -> bool:
        """
        Validate generator type name.

        Must match pattern: ^[a-z][a-z0-9_-]*$

        Args:
            generator_type: Type name to validate

        Returns:
            True if valid, False otherwise
        """
        import re

        pattern = r"^[a-z][a-z0-9_-]*$"
        return bool(re.match(pattern, generator_type))

    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance (primarily for testing).

        Warning: This will clear all registered generators.
        """
        with cls._lock:
            cls._instance = None
