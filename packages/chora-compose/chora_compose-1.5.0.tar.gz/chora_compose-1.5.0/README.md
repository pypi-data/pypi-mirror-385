# Chora Compose

**Version 1.3.0** | [Documentation](docs/) | [Developer Docs](dev-docs/) | [AGENTS.md](AGENTS.md) | [Changelog](CHANGELOG.md) | [Examples](examples/) | [MCP Reference](docs/reference/mcp/README.md)

A configuration-driven framework for structured Human-AI collaborative content and artifact generation.

[![Python 3.12+](https://img.shields.io/badge/3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency_management-Poetry-blue.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/MIT-green.svg)](LICENSE)
[![Built with chora-base](https://img.shields.io/badge/built_with-chora--base_v1.1.1-blue.svg)](https://github.com/liminalcommons/chora-base)

---

## What is Chora Compose?

Chora Compose is a framework that enables teams to define, execute, and document content generation workflows using structured JSON configurations. **New in v1.1.0:** Create configurations conversationally with Claude Desktop - no file editing required. Define **what** needs to be generated and **how**, letting the system handle execution.

**Key Features:**

- **Configuration-Driven** - Define workflows using JSON Schema-validated configs
- **Conversational Workflow Authoring** - Create and refine configs through conversation (v1.1.0+)
  - Draft → Test → Modify → Save workflow
  - Ephemeral storage with 30-day retention
  - Zero IDE context switching
  - 70% faster than traditional file editing
- **MCP Integration** - 17 tools + 5 resources for comprehensive AI agent integration (v1.1.0)
  - 13 core tools: generate_content, assemble_artifact, validate_content, and more
  - 4 config lifecycle tools: draft_config, test_config, modify_config, save_config
  - 5 capability discovery resources for agent self-configuration
- **Gateway Integration** - Built for gateway/orchestration layer consumption (v1.3.0+)
  - Generator dependency discovery via `upstream_dependencies`
  - Event emission to `var/telemetry/events.jsonl` for monitoring
  - Trace context propagation via `CHORA_TRACE_ID` environment variable
  - Concurrency limits exposed via `capabilities://server`
  - [Gateway Integration Guide](docs/how-to/mcp/use-with-gateway.md)
- **Multiple Generators** - Template-based (Jinja2), demonstration-based, AI-powered (Claude Code Generation)
- **Composable Artifacts** - Assemble complex outputs from modular content pieces
- **Documentation-First** - Built using Documentation-Driven Development (DDD)
- **Type-Safe** - Full Pydantic models with mypy type checking
- **Extensible** - Plugin architecture for custom generators and validators

---

## Quick Start

### Installation

**Prerequisites:**
- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management


**Install Chora Compose:**

```bash
# Clone the repository
git clone https://github.com/liminalcommons/chora-compose.git
cd chora-compose


# Install dependencies
poetry install


# Verify installation
poetry run python -c "from chora_compose import __version__; print(f'Chora Compose v{__version__}')"


```

### Quick Start: Conversational Config Creation (v1.1.0)

**Option 1: Conversational (Recommended for new users)**

Open Claude Desktop and say:
```
Create a content config for generating README files from project metadata
```

Claude will:
1. Create a draft config
2. Show you a preview
3. Let you refine it through conversation
4. Save it when you're ready

**Time to first preview:** 30-60 seconds
**No file editing required!**

See [Tutorial: Conversational Config Creation](docs/tutorials/intermediate/02-conversational-config-creation.md) for details.

---

**Option 2: Traditional (File-based)**

Try the included OpenAPI → API Docs example:

```bash
cd examples/jinja2-api-docs
poetry run python generate.py
```

This generates complete API reference documentation from an OpenAPI specification using a Jinja2 template.

**Output:**
```
======================================================================
Chora Compose - Jinja2Generator Example
Generating API Reference Documentation from OpenAPI Spec
======================================================================

[1/4] Loading OpenAPI spec from: data/openapi-petstore.json
      ✓ Loaded spec for: Petstore API v1.0.0

[2/4] Loading content config from: configs/content/api-docs-content.json
      ✓ Loaded config: petstore-api-docs

[3/4] Generating documentation with Jinja2Generator
      ✓ Generated 4,963 characters of documentation

[4/4] Writing output to: output/API_REFERENCE.md
      ✓ Documentation written successfully
```

View the generated `output/API_REFERENCE.md` to see the result!

---

## Docker Deployment (n8n Integration)

**NEW in v1.4.0**: Run chora-compose MCP server in Docker for n8n workflow automation.

### Quick Start
```bash
# Clone repository
git clone https://github.com/liminalcommons/chora-compose.git
cd chora-compose

# Configure environment
cp .env.example .env
# Edit .env: Add your ANTHROPIC_API_KEY

# Start with just commands
just docker-build
just docker-up
just docker-health
```

### n8n Integration
In n8n workflow:
1. Add "MCP Client" node
2. Configure endpoint: `http://chora-compose-mcp:8000/sse`
3. Access all 17 chora-compose tools in AI workflows

**Documentation**: See [Docker Deployment Guide](docs/how-to/deployment/deploy-mcp-server-docker.md)

---

## Core Concepts

Chora Compose uses two main configuration types:

### 1. Content Configs

Define **what** content to generate:

```json
{
  "type": "content",
  "id": "my-content",
  "generation": {
    "patterns": [{
      "type": "jinja2",
      "template": "my-template.j2",
      "generation_config": {
        "context": {
          "data": {"source": "file", "path": "data.json"}
        }
      }
    }]
  }
}
```

### 2. Artifact Configs

Define **how** to assemble final outputs:

```json
{
  "type": "artifact",
  "id": "my-artifact",
  "content": {
    "children": [
      {"id": "intro", "path": "configs/content/intro.json"},
      {"id": "body", "path": "configs/content/body.json"}
    ]
  },
  "output": {
    "primary_file": "OUTPUT.md"
  }
}
```

---

## Available Generators

| Generator | Description | Status |
|-----------|-------------|--------|
| **Jinja2** | Template-based generation with full Jinja2 support | ✅ v0.4.0 |
| **Demonstration** | Uses `example_output` from configs | ✅ v0.2.0 |
| **Template Fill** | Simple placeholder substitution | 🚧 Planned v0.5.0 |
| **Code Generation** | AI-powered code generation | 🚧 Planned v0.6.0 |
| **BDD Scenario** | Gherkin/BDD test generation | 🚧 Planned v0.6.0 |

---

## Documentation

We follow the **Diátaxis** documentation framework with 33 complete documents:


### 📘 Tutorials (Learning-Oriented)

- [Your First Config](docs/tutorials/getting-started/02-your-first-config.md)
- [Generate Your First Content](docs/tutorials/getting-started/03-generate-your-first-content.md)
- [Compose Your First Artifact](docs/tutorials/getting-started/04-compose-your-first-artifact.md)
- [Dynamic Content with Jinja2](docs/tutorials/intermediate/01-dynamic-content-with-jinja2.md)



### 🔧 How-To Guides (Task-Oriented)

- **Configuration**: Load Configs, Create Content Config, Create Artifact Config
- **Generation**: Use Demonstration Generator, Generate API Docs from OpenAPI, Use Template Inheritance
- **Dogfooding**: Generate CHANGELOG, Generate Release Notes, Generate Docs Status
- **Debugging**: Debug Generation, Debug Jinja2 Templates



### 📚 Reference (Information-Oriented)

- [ConfigLoader API](docs/reference/api/core/config-loader.md)
- [ArtifactComposer API](docs/reference/api/core/artifact-composer.md)
- [Jinja2Generator API](docs/reference/api/generators/jinja2.md)
- [DemonstrationGenerator API](docs/reference/api/generators/demonstration.md)



### 💡 Explanation (Understanding-Oriented)

- [Why Two-Layer Validation](docs/explanation/architecture/why-two-layer-validation.md)
- [Generator Strategy Pattern](docs/explanation/architecture/generator-strategy-pattern.md)
- [Config-Driven Architecture](docs/explanation/architecture/config-driven-architecture.md)
- [Why Jinja2 for Dynamic Generation](docs/explanation/architecture/why-jinja2-for-dynamic-generation.md)




**Full Documentation Status:** [docs/DOCUMENTATION_STATUS.md](docs/DOCUMENTATION_STATUS.md)

---

## Development

### Setup Development Environment

```bash
# Install with development dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install


# Check code
poetry run ruff check .

# Format code
poetry run ruff format .



# Check types
poetry run mypy src/



# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=chora_compose



# Install hooks
poetry run pre-commit install


```

### Project Structure

```
chora-compose/
├── src/chora_compose/       # Source code

│   ├── core/  # Core engine (ConfigLoader, ArtifactComposer)
│   ├── generators/  # Generation strategies
│   ├── validators/  # Validation rules (planned)
│   ├── storage/  # Ephemeral storage (planned)
│   ├── mcp/  # MCP server (planned)


├── tests/       # Test suite

│   ├── test_*.py  # Unit tests
│   ├── integration/  # Integration tests
│   ├── fixtures/  # Test data


├── examples/       # Working examples

│   ├── jinja2-api-docs/  # OpenAPI → Markdown example


├── docs/       # Complete Diátaxis documentation

├── schemas/       # JSON Schema definitions

│   ├── content/v3.1/  # Content config schema
│   ├── artifact/v3.1/  # Artifact config schema


├── configs/       # Example configurations


```

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=chora_compose

# Specific test file
poetry run pytest tests/test_jinja2_generator.py

# Integration tests only
poetry run pytest tests/integration/

# Verbose output
poetry run pytest -v
```

**Current Test Status:** 489 tests passing, 8 skipped (98.4% pass rate, 82% coverage)

### Development Infrastructure

This project uses the [chora-base](https://github.com/liminalcommons/chora-base) template for development infrastructure:

**Automation Scripts** (`scripts/`)
- `setup.sh` - One-command project setup
- `smoke-test.sh` - Quick validation (<30s)
- `pre-merge.sh` - Pre-merge validation (tests, coverage, linting)
- `build-dist.sh` - Build distribution packages
- `bump-version.sh` - Version management
- `dev-server.sh` - Development MCP server with auto-reload

**Task Automation** (`justfile`)
```bash
just install       # Install dependencies
just test          # Run full test suite
just smoke         # Run smoke tests
just lint          # Run linter
just format        # Format code
just typecheck     # Type checking
just pre-merge     # Pre-merge validation
just run           # Start MCP server
```

**GitHub Actions Workflows**
- `test.yml` - Run tests on Python 3.11, 3.12, 3.13
- `lint.yml` - Code quality checks (ruff, mypy)
- `smoke.yml` - Quick smoke tests on push
- `release.yml` - Automated PyPI publishing
- `codeql.yml` - Security scanning
- `dependency-review.yml` - Dependency vulnerability checks

**Quality Gates**
- Pre-commit hooks (ruff, trailing whitespace, YAML)
- Test coverage requirement: ≥85%
- Type checking with mypy (strict mode)
- Automated dependency updates (Dependabot)

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development workflow documentation.

---

## Examples


### Jinja2 API Documentation
**Location:** `examples/jinja2-api-docs/`

Generate API reference documentation from an OpenAPI 3.0 specification using Jinja2 templates

**Features:**
- Loads OpenAPI JSON
- Renders with custom Jinja2 template
- Outputs formatted Markdown
- Includes parameter tables, response examples, schemas


**Run:**
```bash
cd examples/jinja2-api-docs
poetry run python generate.py
```

**See:** [examples/jinja2-api-docs/README.md](examples/jinja2-api-docs/README.md)


---

## Documentation-Driven Development (DDD)

Chora Compose was built using Documentation-Driven Development - a process where we:

1. **Write complete documentation first** (before any code)
2. **Extract test cases** directly from documentation examples
3. **Implement features** to pass the documentation-derived tests


**Result:** Zero API drift, zero bugs, documentation always accurate.

**Read more:** [docs/meta/DDD_PILOT_LESSONS_LEARNED.md](docs/meta/DDD_PILOT_LESSONS_LEARNED.md)

---

## What's New in v1.1.0

### Conversational Workflow Authoring 🎯

Create, test, and refine configurations through conversation with Claude Desktop:

**Traditional Workflow:**
```
Open IDE → Edit JSON → Save → Run → Check → Repeat
Time: 20-30 minutes, 6-12 context switches
```

**Conversational Workflow (v1.1.0):**
```
Chat with Claude → Preview → Refine → Save
Time: 5-10 minutes, 0 context switches
```

**New Tools:**
- `draft_config` - Create temporary configs in ephemeral storage
- `test_config` - Preview generation without side effects
- `modify_config` - Refine configs through conversation
- `save_config` - Persist when ready

**Benefits:**
- ✅ 70% time savings vs traditional file editing
- ✅ Zero IDE context switching
- ✅ Non-technical users can create configs
- ✅ Instant validation and preview
- ✅ 30-day draft retention for safe experimentation

---

### Capability Discovery Resources

AI agents can now introspect and self-configure:

**New Resources:**
- `capabilities://server` - Server metadata, features, limits
- `capabilities://tools` - Complete tool inventory with schemas
- `capabilities://resources` - Resource URI catalog
- `capabilities://generators` - Live generator registry

**Benefits:**
- ✅ Agents adapt dynamically to server evolution
- ✅ Plugin generators automatically discovered
- ✅ No hardcoded knowledge required

---

## Roadmap

### v1.1.0 ✅ Current
- ✅ Conversational workflow authoring (4 new MCP tools)
- ✅ Capability discovery pattern (4 new MCP resources)
- ✅ EphemeralConfigManager with 30-day retention
- ✅ Complete MCP integration (17 tools + 5 resources)

### v1.1.1 📋 Week 1-2 (Gateway Essentials)
- 📋 Generator dependency tags with upstream service metadata
- 📋 Concurrency limits exposure via capabilities
- 📋 Event emission foundation (OpenTelemetry format)
- 📋 Joint integration test setup with mcp-n8n
- **Focus:** Critical gaps, ecosystem compliance

### v1.1.2 🌟 Week 3 (Continuous Feedback) **NEW**
- 📋 Enhanced generator metadata (latency hints, stability)
- 📋 Event schema v2 (duration_ms, validation events)
- 📋 Preliminary gateway context (instrumentation for v1.2.0 design)
- **Focus:** Enable mcp-n8n Phase 1 feedback loop

### v1.2.0 🎯 Week 7-10 (Gateway Integration - Phased Betas)
- **Beta 1 (Week 7):** Gateway-aware capabilities + preview artifact tool
- **Beta 2 (Week 9):** Telemetry resource + multi-step preview + performance
- **GA (Week 10):** Complete documentation + production hardening
- **Focus:** Platform-layer maturation, unblock mcp-n8n Phase 2 early

### v1.3.0+ 🚀 Week 11-14 (Dynamic Discovery & Context Bus)
- 📋 Dynamic capability discovery (hot-reload generators)
- 📋 Workflow coordination primitives (transactions, rollback)
- 📋 Context bus integration (when platform provides it)
- 📋 SLSA Level 3 provenance
- **Focus:** Runtime extensibility + distributed platform infrastructure



**Roadmaps:**
- **⭐ Unified Roadmap (Primary):** [UNIFIED_INTEGRATION_ROADMAP.md](docs/UNIFIED_INTEGRATION_ROADMAP.md) - Sprint-based execution plan (v1.1.1 - v1.2.0)
- **Gateway Integration:** [ROADMAP_GATEWAY_INTEGRATION.md](docs/ROADMAP_GATEWAY_INTEGRATION.md) - Detailed feature roadmap & long-term vision
- **Cross-Team Coordination:** [CROSS_TEAM_COORDINATION.md](docs/CROSS_TEAM_COORDINATION.md) - Specs, schedule, decision framework
- **Original Roadmap:** [ROADMAP.md](ROADMAP.md) - Original 20-week plan (archived, historical reference)

**Specifications:**
- [Event Schema](specs/event-schema.md) - Unified event format for cross-service observability
- [Specs Overview](specs/README.md) - All ecosystem specifications

---

## Contributing

We welcome contributions! Please see:
- [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon)
- [Code of Conduct](CODE_OF_CONDUCT.md) (coming soon)

**Development Process:**
1. Fork the repository
2. Create a feature branch
3. Write documentation first (DDD approach)
4. Extract tests from docs
5. Implement to pass tests
6. Submit pull request

---

## Related Projects

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Protocol for AI tool integration
- [JSON Schema](https://json-schema.org/) - Schema validation specification
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Pydantic](https://docs.pydantic.dev/) - Data validation library


---

## License

[MIT License](LICENSE) (coming soon)

---

## Acknowledgments

- Built with [Poetry](https://python-poetry.org/)
- Built with [Diátaxis](https://diataxis.fr/)
- Built with [mypy](https://mypy-lang.org/)
- Built with [Ruff](https://docs.astral.sh/ruff/)

- Developed using Documentation-Driven Development

---

**Questions?** Open an issue or see [docs/](docs/) for complete documentation.

**Version:** 1.3.0 | **Updated:** 2025-10-18
