"""Pydantic models for Chora Compose configuration files."""

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# Enums for constrained string values
class GenerationFrequency(str, Enum):
    """How often content should be regenerated."""

    MANUAL = "manual"
    ON_DEMAND = "on_demand"
    SCHEDULED = "scheduled"
    CONTINUOUS = "continuous"


class OutputFormat(str, Enum):
    """Expected output format of generated content."""

    MARKDOWN = "markdown"
    JSON = "json"
    YAML = "yaml"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GHERKIN = "gherkin"
    TEXT = "text"
    HTML = "html"
    XML = "xml"


class GenerationSource(str, Enum):
    """Primary source of element content."""

    AI = "ai"
    HUMAN = "human"
    TEMPLATE = "template"
    MIXED = "mixed"


class ReviewStatus(str, Enum):
    """Human review status of generated content."""

    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"


class SourceType(str, Enum):
    """Type of input source."""

    CONTENT_CONFIG = "content_config"
    ARTIFACT_CONFIG = "artifact_config"
    EPHEMERAL_OUTPUT = "ephemeral_output"
    EXTERNAL_FILE = "external_file"
    GIT_REFERENCE = "git_reference"
    INLINE_DATA = "inline_data"
    REQUIREMENT_ID = "requirement_id"


class ElementFormat(str, Enum):
    """Format type of content element."""

    MARKDOWN = "markdown"
    CODE = "code"
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    GHERKIN = "gherkin"
    SECTION = "section"


class KnownGeneratorTypes:
    """
    Known generator types for IDE support and backward compatibility.

    Note: The system now accepts ANY valid generator type string
    (matching pattern ^[a-z][a-z0-9_-]*$). These constants are provided
    for convenience and IDE autocomplete.
    """

    DEMONSTRATION = "demonstration"
    JINJA2 = "jinja2"
    TEMPLATE_FILL = "template_fill"
    CODE_GENERATION = "code_generation"
    BDD_SCENARIO_ASSEMBLY = "bdd_scenario_assembly"
    CUSTOM = "custom"


class ValidationCheckType(str, Enum):
    """Type of validation check."""

    PRESENCE = "presence"
    FORMAT = "format"
    LINT = "lint"
    SYNTAX = "syntax"
    CUSTOM = "custom"


class ValidationSeverity(str, Enum):
    """Severity level of validation failure."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class EvolutionStage(str, Enum):
    """Lifecycle stage of config."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class EvolutionEventType(str, Enum):
    """Type of evolution event."""

    CREATION = "creation"
    UPDATE = "update"
    APPROVAL = "approval"
    DEPRECATION = "deprecation"


# Content Configuration Models


class SchemaRef(BaseModel):
    """Reference to a schema version."""

    id: str = Field(description="Schema identifier")
    version: str = Field(
        pattern=r"^\d+\.\d+(\.\d+)?$", description="Schema version (semver)"
    )


class ContentMetadata(BaseModel):
    """Metadata for content configuration."""

    description: str = Field(
        min_length=1, max_length=500, description="Brief description of content config"
    )
    version: str = Field(
        pattern=r"^\d+\.\d+\.\d+$", description="Content config version (semver)"
    )
    generation_frequency: GenerationFrequency = Field(
        default=GenerationFrequency.MANUAL, description="How often to regenerate"
    )
    output_format: Optional[OutputFormat] = Field(
        default=None, description="Expected output format"
    )


class Instructions(BaseModel):
    """Guidance for content generation."""

    global_: Optional[str] = Field(
        default=None, alias="global", description="High-level guidance for all elements"
    )
    system_prompt: Optional[str] = Field(
        default=None, description="System-level prompt for AI generation"
    )
    user_prompt: Optional[str] = Field(
        default=None, description="User-level prompt for AI generation"
    )


class InputSource(BaseModel):
    """External input source for generation context."""

    id: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Unique identifier for this source"
    )
    notes: Optional[str] = Field(default=None, description="Description of this source")
    source_type: SourceType = Field(description="Type of source")
    source_locator: str = Field(
        min_length=1, description="Identifier to find the source"
    )
    data_selector: Optional[str] = Field(
        default=None, description="What data to extract from source"
    )
    required: bool = Field(
        default=True, description="Whether this input is required for generation"
    )


class Inputs(BaseModel):
    """Input sources configuration."""

    sources: list[InputSource] = Field(
        default_factory=list, description="Array of input sources"
    )


class EphemeralStorage(BaseModel):
    """Configuration for ephemeral storage."""

    basePath: Optional[str] = Field(
        default=None, description="Base directory for ephemeral storage"
    )
    subfolderPattern: Optional[str] = Field(
        default=None, description="Pattern for subfolder structure"
    )
    filenamePattern: Optional[str] = Field(
        default=None, description="Pattern for ephemeral filenames"
    )
    format: Literal["json", "yaml", "text"] = Field(
        default="json", description="Format for ephemeral files"
    )


class ContentElement(BaseModel):
    """Individual content element to generate."""

    name: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$",
        description="Unique name for this element within config",
    )
    description: Optional[str] = Field(
        default=None, description="Description of what this element represents"
    )
    prompt_guidance: Optional[str] = Field(
        default=None, description="Specific guidance for generating this element"
    )
    format: ElementFormat = Field(description="Format type of this element")
    output_format: Optional[str] = Field(
        default=None, description="Specific output format (e.g., 'python' for code)"
    )
    example_output: Optional[str] = Field(
        default=None, description="Example or actual output content"
    )
    generation_source: Optional[GenerationSource] = Field(
        default=None, description="Primary source of element content"
    )
    review_status: ReviewStatus = Field(
        default=ReviewStatus.PENDING, description="Human review status"
    )
    human_feedback: Optional[str] = Field(
        default=None, description="Reviewer notes or revision requests"
    )


class ChildReference(BaseModel):
    """Reference to a child content config."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", description="ID of child config")
    path: str = Field(description="Path to child config file")
    required: bool = Field(default=True, description="Whether child is required")
    order: Optional[float] = Field(default=None, ge=0, description="Processing order")
    version: Optional[str] = Field(
        default=None,
        pattern=r"^\d+\.\d+(\.\d+)?$",
        description="Specific version to use",
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")
    conditions: Optional[str] = Field(
        default=None, description="Conditional logic for inclusion"
    )


class GenerationVariable(BaseModel):
    """Variable mapping for template generation."""

    name: str = Field(
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="Variable name for substitution",
    )
    variableType: Literal["string", "number", "boolean", "array", "object"] = Field(
        default="string", description="Data type of variable"
    )
    source: str = Field(description="Where to pull data from (e.g., 'elements.<name>')")
    default: Optional[str] = Field(
        default=None, description="Default value if source unavailable"
    )


class GenerationPattern(BaseModel):
    """Pattern describing how to generate content."""

    id: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Unique identifier for this pattern"
    )
    type: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Generation strategy type"
    )
    template: Optional[str] = Field(
        default=None, description="Text template with placeholders"
    )
    variables: list[GenerationVariable] = Field(
        default_factory=list, description="Variable mappings for template"
    )
    generation_config: Optional[dict[str, Any]] = Field(
        default=None, description="Type-specific configuration"
    )


class Generation(BaseModel):
    """Generation configuration."""

    patterns: list[GenerationPattern] = Field(
        default_factory=list, description="Array of generation patterns"
    )


class ValidationRule(BaseModel):
    """Validation rule for content quality."""

    id: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Unique identifier for this rule"
    )
    check_type: ValidationCheckType = Field(description="Type of validation")
    target: str = Field(description="What to check")
    check_config: Optional[dict[str, Any]] = Field(
        default=None, description="Type-specific configuration"
    )
    threshold: Optional[float] = Field(
        default=None, ge=0, description="Threshold for quantitative checks"
    )
    severity: ValidationSeverity = Field(
        default=ValidationSeverity.ERROR, description="Severity if rule fails"
    )


class Validation(BaseModel):
    """Validation configuration."""

    rules: list[ValidationRule] = Field(
        default_factory=list, description="Array of validation rules"
    )


class StateTracking(BaseModel):
    """State tracking configuration."""

    history: bool = Field(default=False, description="Track generation history")
    versioning: bool = Field(default=False, description="Maintain version history")


class State(BaseModel):
    """State configuration."""

    tracking: Optional[StateTracking] = Field(
        default=None, description="Tracking configuration"
    )


class EvolutionEvent(BaseModel):
    """Evolution history event."""

    date: str = Field(description="Date of change (ISO 8601 format)")
    type: EvolutionEventType = Field(description="Type of evolution event")
    description: str = Field(description="Description of the change")
    rationale: Optional[str] = Field(default=None, description="Reason for change")


class Evolution(BaseModel):
    """Evolution tracking configuration."""

    stage: EvolutionStage = Field(
        default=EvolutionStage.DRAFT, description="Current lifecycle stage"
    )
    history: list[EvolutionEvent] = Field(
        default_factory=list, description="History of changes"
    )


class ContentConfig(BaseModel):
    """Complete content configuration."""

    type: Literal["content"] = Field(description="Discriminator for content config")
    id: str = Field(
        pattern=r"^[a-z][a-z0-9-]*$",
        description="Unique identifier using kebab-case",
    )
    schemaRef: SchemaRef = Field(description="Schema version reference")
    metadata: ContentMetadata = Field(description="Content metadata")
    instructions: Optional[Instructions] = Field(
        default=None, description="Generation instructions"
    )
    inputs: Optional[Inputs] = Field(default=None, description="Input sources")
    ephemeralStorage: Optional[EphemeralStorage] = Field(
        default=None, description="Ephemeral storage configuration"
    )
    elements: list[ContentElement] = Field(
        min_length=1, description="Array of content elements"
    )
    children: list[ChildReference] = Field(
        default_factory=list, description="Child config references"
    )
    generation: Optional[Generation] = Field(
        default=None, description="Generation configuration"
    )
    validation: Optional[Validation] = Field(
        default=None, description="Validation configuration"
    )
    state: Optional[State] = Field(default=None, description="State configuration")
    evolution: Optional[Evolution] = Field(
        default=None, description="Evolution tracking"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID follows kebab-case pattern."""
        if not v or not v[0].islower():
            raise ValueError("ID must start with lowercase letter")
        return v


# Artifact Configuration Models


class ArtifactType(str, Enum):
    """Category of artifact."""

    DOCUMENTATION = "documentation"
    TEST = "test"
    CODE = "code"
    CONFIGURATION = "configuration"
    REPORT = "report"
    MIXED = "mixed"


class ArtifactOutputFormat(str, Enum):
    """General format category of output."""

    MARKDOWN = "markdown"
    CODE = "code"
    BINARY = "binary"
    BDD = "bdd"
    TEST_RESULTS = "test_results"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    HTML = "html"
    XML = "xml"


class CompositionStrategy(str, Enum):
    """Strategy for combining content sources."""

    CONCAT = "concat"
    MERGE = "merge"
    TEMPLATE = "template"
    CUSTOM = "custom"


class RetrievalStrategy(str, Enum):
    """How to retrieve ephemeral content."""

    LATEST = "latest"
    ALL = "all"
    VERSION = "version"
    APPROVED_ONLY = "approved_only"


class ExpectedSource(str, Enum):
    """Expected source for content."""

    AI = "ai"
    HUMAN = "human"
    TEMPLATE = "template"
    MIXED = "mixed"
    ANY = "any"


class DependencyType(str, Enum):
    """Type of dependency."""

    ARTIFACT = "artifact"
    EXTERNAL_SYSTEM = "external_system"
    REQUIREMENT = "requirement"
    CODE_MODULE = "code_module"


class DependencyRelationship(str, Enum):
    """Relationship type between artifacts."""

    TESTS = "tests"
    IMPLEMENTS = "implements"
    DOCUMENTS = "documents"
    BASED_ON = "based_on"
    RELATED_TO = "related_to"
    REQUIRES = "requires"


class ArtifactOutput(BaseModel):
    """Output file specification."""

    file: str = Field(description="Path/URI for final artifact output")
    format: ArtifactOutputFormat = Field(description="General format category")
    language_dialect: Optional[str] = Field(
        default=None, description="Specific language or dialect"
    )
    encoding: str = Field(default="utf-8", description="File encoding")


class ArtifactMetadata(BaseModel):
    """Metadata for artifact configuration."""

    title: str = Field(min_length=1, max_length=200, description="Human-readable title")
    type: Optional[ArtifactType] = Field(
        default=None, description="Category of artifact"
    )
    version: Optional[str] = Field(
        default=None,
        pattern=r"^\d+\.\d+\.\d+$",
        description="Artifact config version (semver)",
    )
    purpose: str = Field(
        min_length=1, max_length=1000, description="Explanation of artifact purpose"
    )
    description: Optional[str] = Field(
        default=None, description="Additional description"
    )
    outputs: list[ArtifactOutput] = Field(
        min_length=1, description="Array of output files"
    )
    compositionStrategy: CompositionStrategy = Field(
        default=CompositionStrategy.CONCAT,
        description="Strategy for combining content",
    )


class ContentChildReference(BaseModel):
    """Reference to content config for artifact."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", description="Content config ID")
    path: str = Field(description="Path to content config file")
    required: bool = Field(default=True, description="Whether content is required")
    order: Optional[float] = Field(default=None, ge=0, description="Assembly order")
    version: Optional[str] = Field(
        default=None,
        pattern=r"^\d+\.\d+(\.\d+)?$",
        description="Specific version to use",
    )
    notes: Optional[str] = Field(default=None, description="Additional notes")
    retrievalStrategy: RetrievalStrategy = Field(
        default=RetrievalStrategy.LATEST, description="How to retrieve content"
    )
    conditions: Optional[str] = Field(
        default=None, description="Conditional inclusion logic"
    )
    expected_source: ExpectedSource = Field(
        default=ExpectedSource.ANY, description="Expected source for workflow guidance"
    )
    review_required: bool = Field(
        default=False, description="Whether human review is mandatory"
    )


class Content(BaseModel):
    """Content configuration for artifact."""

    children: list[ContentChildReference] = Field(
        min_length=1, description="Array of content config references"
    )


class Dependency(BaseModel):
    """Dependency on other artifact or system."""

    id: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Unique identifier for dependency"
    )
    type: DependencyType = Field(description="Type of dependency")
    locator: str = Field(min_length=1, description="Identifier for the dependency")
    relationship: DependencyRelationship = Field(
        description="Relationship to dependency"
    )
    notes: Optional[str] = Field(default=None, description="Description of dependency")


class ArtifactValidationCheckType(str, Enum):
    """Type of artifact validation."""

    COMPLETENESS = "completeness"
    COHERENCE = "coherence"
    FORMAT = "format"
    LINT = "lint"
    CUSTOM_CHECK = "custom_check"


class ArtifactValidationRule(BaseModel):
    """Validation rule for artifact."""

    id: str = Field(
        pattern=r"^[a-z][a-z0-9_-]*$", description="Unique identifier for rule"
    )
    check_type: ArtifactValidationCheckType = Field(description="Type of validation")
    target: str = Field(description="What to check")
    check_config: Optional[dict[str, Any]] = Field(
        default=None, description="Type-specific configuration"
    )
    severity: ValidationSeverity = Field(
        default=ValidationSeverity.ERROR, description="Severity if rule fails"
    )


class ArtifactValidation(BaseModel):
    """Artifact validation configuration."""

    rules: list[ArtifactValidationRule] = Field(
        default_factory=list, description="Array of validation rules"
    )


class ArtifactConfig(BaseModel):
    """Complete artifact configuration."""

    type: Literal["artifact"] = Field(description="Discriminator for artifact config")
    id: str = Field(
        pattern=r"^[a-z][a-z0-9-]*$",
        description="Unique identifier using kebab-case",
    )
    schemaRef: SchemaRef = Field(description="Schema version reference")
    metadata: ArtifactMetadata = Field(description="Artifact metadata")
    content: Content = Field(description="Content configuration")
    dependencies: list[Dependency] = Field(
        default_factory=list, description="Dependencies on other artifacts/systems"
    )
    state: Optional[State] = Field(default=None, description="State configuration")
    validation: Optional[ArtifactValidation] = Field(
        default=None, description="Validation configuration"
    )
    evolution: Optional[Evolution] = Field(
        default=None, description="Evolution tracking"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID follows kebab-case pattern."""
        if not v or not v[0].islower():
            raise ValueError("ID must start with lowercase letter")
        return v
