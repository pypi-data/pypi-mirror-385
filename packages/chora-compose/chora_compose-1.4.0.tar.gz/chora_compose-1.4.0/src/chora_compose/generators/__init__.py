"""Content generators for Chora Compose."""

from chora_compose.generators.base import GeneratorStrategy
from chora_compose.generators.bdd_scenario import (
    BDDScenarioError,
    BDDScenarioGenerator,
)
from chora_compose.generators.demonstration import DemonstrationGenerator
from chora_compose.generators.jinja2 import GenerationError, Jinja2Generator
from chora_compose.generators.registry import GeneratorRegistry, RegistryError
from chora_compose.generators.template_fill import (
    TemplateFillError,
    TemplateFillGenerator,
)

# Code generation is optional (requires anthropic package)
try:
    from chora_compose.generators.code_generation import (
        CodeGenerationError,  # noqa: F401
        CodeGenerationGenerator,  # noqa: F401
    )

    _has_code_generation = True
except ImportError:
    _has_code_generation = False

__all__ = [
    "GeneratorStrategy",
    "DemonstrationGenerator",
    "Jinja2Generator",
    "TemplateFillGenerator",
    "BDDScenarioGenerator",
    "GenerationError",
    "TemplateFillError",
    "BDDScenarioError",
    "GeneratorRegistry",
    "RegistryError",
]

if _has_code_generation:
    __all__.extend(["CodeGenerationGenerator", "CodeGenerationError"])
