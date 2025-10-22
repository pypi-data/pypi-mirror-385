"""Artifact composer for assembling final output files."""

import time
from pathlib import Path
from typing import Any, Optional

from chora_compose.core.config_loader import ConfigLoader
from chora_compose.core.context_resolver import ContextResolver
from chora_compose.core.data_selector import DataSelector
from chora_compose.core.models import (
    CompositionStrategy,
    ContentConfig,
    KnownGeneratorTypes,
)
from chora_compose.generators.registry import GeneratorRegistry
from chora_compose.storage.ephemeral import EphemeralStorageManager
from chora_compose.telemetry import ArtifactAssembledEvent, emit_event


class CompositionError(Exception):
    """Raised when artifact composition fails."""

    pass


class ArtifactComposer:
    """
    Composes final artifacts by loading content configs and generating output.

    The composer orchestrates the full workflow:
    1. Loads artifact configuration
    2. Resolves and loads all referenced content configs
    3. Generates content for each config using appropriate generator
    4. Composes all content according to composition strategy
    5. Writes final output to specified file(s)
    """

    def __init__(
        self,
        config_loader: Optional[ConfigLoader] = None,
        storage_manager: Optional[EphemeralStorageManager] = None,
        context_resolver: Optional[ContextResolver] = None,
        data_selector: Optional[DataSelector] = None,
        base_path: Optional[Path] = None,
    ) -> None:
        """
        Initialize composer with Phase 2 components.

        Args:
            config_loader: ConfigLoader instance (creates new one if not provided)
            storage_manager: Optional ephemeral storage manager
            context_resolver: Optional context resolver (creates if not provided)
            data_selector: Optional data selector (creates if not provided)
            base_path: Base path for resolving relative paths
        """
        self.loader = config_loader or ConfigLoader()
        self.storage_manager = storage_manager
        self.base_path = base_path or Path.cwd()

        # Initialize context resolver if not provided
        if context_resolver:
            self.context_resolver = context_resolver
        else:
            self.context_resolver = ContextResolver(
                config_loader=self.loader,
                storage_manager=self.storage_manager,
                base_path=self.base_path,
            )

        # Initialize data selector if not provided
        self.data_selector = data_selector or DataSelector()

        # Use the global generator registry
        self.registry = GeneratorRegistry()

    def assemble(
        self,
        artifact_id: str,
        artifact_path: Optional[Path] = None,
        output_override: Optional[Path] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> Path:
        """
        Assemble an artifact from its configuration.

        Args:
            artifact_id: ID of the artifact to assemble
            artifact_path: Optional direct path to artifact config
            output_override: Optional override for output file path
            context: Optional context to pass to child content generation

        Returns:
            Path to the generated output file

        Raises:
            CompositionError: If composition fails
        """
        start_time = time.time()
        status = "success"
        error_message = None
        section_count = 0
        output_path = None

        try:
            # Load artifact config
            try:
                if artifact_path:
                    artifact_config = self.loader.load_artifact_config(
                        artifact_id, config_path=artifact_path
                    )
                else:
                    artifact_config = self.loader.load_artifact_config(artifact_id)
            except Exception as e:
                raise CompositionError(f"Failed to load artifact config: {e}") from e

            # Generate content for each child
            contents = []
            for child in sorted(
                artifact_config.content.children, key=lambda c: c.order or 0
            ):
                try:
                    content = self._generate_child_content(
                        child.path, child.id, context
                    )
                    contents.append(content)
                except Exception as e:
                    if child.required:
                        raise CompositionError(
                            f"Failed to generate required content '{child.id}': {e}"
                        ) from e
                    # Skip optional content that fails
                    continue

            section_count = len(contents)

            # Compose all content
            final_content = self._compose_content(
                contents, artifact_config.metadata.compositionStrategy
            )

            # Determine output path
            if output_override:
                output_path = output_override
            else:
                # Use first output file from config
                if not artifact_config.metadata.outputs:
                    raise CompositionError(
                        f"Artifact '{artifact_id}' has no output files defined"
                    )
                output_file = artifact_config.metadata.outputs[0].file
                output_path = Path(output_file)

            # Write output
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(final_content, encoding="utf-8")
            except Exception as e:
                raise CompositionError(f"Failed to write output file: {e}") from e

            return output_path

        except Exception as e:
            status = "error"
            error_message = str(e)
            raise
        finally:
            # Emit telemetry event
            duration_ms = int((time.time() - start_time) * 1000)
            emit_event(
                ArtifactAssembledEvent(
                    artifact_config_id=artifact_id,
                    section_count=section_count,
                    status=status,
                    duration_ms=duration_ms,
                    output_path=str(output_path) if output_path else None,
                    error_message=error_message,
                )
            )

    def _generate_child_content(
        self,
        content_path: str,
        content_id: str,
        parent_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Generate content for a single content config.

        Args:
            content_path: Path to content config file
            content_id: ID of content config
            parent_context: Optional context from parent artifact assembly

        Returns:
            Generated content string

        Raises:
            CompositionError: If generation fails
        """
        # Load content config
        path = Path(content_path)
        if not path.is_absolute():
            # Try relative to current directory
            if not path.exists():
                # Try relative to configs directory
                path = Path("configs") / content_path
                if not path.exists():
                    raise CompositionError(f"Content config not found: {content_path}")

        try:
            content_config = self.loader.load_config(path)
            if not isinstance(content_config, ContentConfig):
                raise CompositionError(f"Config at {path} is not a content config")
        except Exception as e:
            raise CompositionError(
                f"Failed to load content config from {path}: {e}"
            ) from e

        # Determine generator type
        generator_type = KnownGeneratorTypes.DEMONSTRATION  # Default
        if (
            content_config.generation
            and content_config.generation.patterns
            and len(content_config.generation.patterns) > 0
        ):
            generator_type = content_config.generation.patterns[0].type

        # Get appropriate generator from registry
        try:
            generator = self.registry.get(generator_type)
        except Exception as e:
            raise CompositionError(
                f"No generator available for type '{generator_type}': {e}"
            ) from e

        # Resolve input sources if config has them (Phase 2 integration)
        # Start with parent context if provided
        context = parent_context.copy() if parent_context else {}
        if hasattr(content_config, "inputs") and content_config.inputs:
            if content_config.inputs.sources:
                try:
                    # Resolve all input sources
                    resolved_inputs = self.context_resolver.resolve(
                        content_config.inputs.sources
                    )

                    # Apply data selectors to resolved sources
                    for source in content_config.inputs.sources:
                        if source.data_selector and source.id in resolved_inputs:
                            resolved_inputs[source.id] = self.data_selector.select(
                                resolved_inputs[source.id], source.data_selector
                            )

                    # Merge resolved inputs with parent context (inputs take precedence)
                    context.update(resolved_inputs)
                except Exception as e:
                    raise CompositionError(
                        f"Failed to resolve inputs for '{content_id}': {e}"
                    ) from e

        # Generate content with resolved context
        try:
            return generator.generate(content_config, context=context)
        except Exception as e:
            raise CompositionError(
                f"Failed to generate content for '{content_id}': {e}"
            ) from e

    def _compose_content(
        self, contents: list[str], strategy: CompositionStrategy
    ) -> str:
        """
        Compose multiple content pieces according to strategy.

        Args:
            contents: List of generated content strings
            strategy: Composition strategy to use

        Returns:
            Composed final content

        Raises:
            CompositionError: If strategy not supported
        """
        if strategy == CompositionStrategy.CONCAT:
            # Simple concatenation
            return "\n\n".join(contents)
        else:
            raise CompositionError(
                f"Composition strategy not yet supported: {strategy}"
            )

    def register_generator(
        self, generation_type: str, generator: object, override: bool = False
    ) -> None:
        """
        Register a custom generator for a generation type.

        Args:
            generation_type: Type of generation this generator handles
            generator: Generator instance implementing GeneratorStrategy
            override: If True, allow overriding existing generators
        """
        from chora_compose.generators.base import GeneratorStrategy

        if not isinstance(generator, GeneratorStrategy):
            raise CompositionError(
                f"Generator must implement GeneratorStrategy, "
                f"got {type(generator).__name__}"
            )
        self.registry.register(generation_type, generator, override=override)
