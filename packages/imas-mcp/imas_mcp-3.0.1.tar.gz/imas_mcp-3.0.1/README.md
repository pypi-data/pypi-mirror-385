# IMAS MCP Server

[![pre-commit][pre-commit-badge]][pre-commit-link]
[![Ruff][ruff-badge]][ruff-link]
[![Python versions][python-badge]][python-link]
[![CI/CD status][build-deploy-badge]][build-deploy-link]
[![Coverage status][codecov-badge]][codecov-link]
[![Documentation][docs-badge]][docs-link]
[![ASV][asv-badge]][asv-link]

A Model Context Protocol (MCP) server providing AI assistants with access to IMAS (Integrated Modelling & Analysis Suite) data structures through natural language search and optimized path indexing.

## Quick Start

Select the setup method that matches your environment:

- HTTP (Hosted): Zero install. Connect to the public endpoint running the latest tagged MCP server from the ITER Organization.
- UV (Local): Install and run in your own Python environment for editable development.
- Docker : Run an isolated container with pre-built indexes.
- Slurm / HPC (STDIO): Launch inside a cluster allocation without opening network ports.

Choose hosted for instant access; choose a local option for customization or controlled resources.

[HTTP](#http-remote-public-endpoint) | [UV](#uv-local-install) | [Docker](#docker-setup) | [Slurm / HPC](#slurm--hpc-stdio)

### HTTP (Remote Public Endpoint)

Connect to the public ITER Organization hosted server—no local install.

#### VS Code (Interactive)

1. `Ctrl+Shift+P` → "MCP: Add Server"
2. Select "HTTP Server"
3. Name: `imas`
4. URL: `https://imas-dd.iter.org/mcp`

#### VS Code (Manual JSON)

Workspace `.vscode/mcp.json` (or inside `"mcp"` in user settings):

```json
{
  "servers": {
    "imas": { "type": "http", "url": "https://imas-dd.iter.org/mcp" }
  }
}
```

#### Claude Desktop config

Pick path for your OS:

Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`  
macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
Linux: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "imas-mcp-hosted": {
      "command": "npx",
      "args": ["mcp-remote", "https://imas-dd.iter.org/mcp"]
    }
  }
}
```

#### OP Client (Pending Clarification)

Placeholder: clarify what "op" refers to (e.g. OpenAI, Operator) to add tailored instructions.

### UV Local Install

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install imas-mcp
# or add to a project env
uv add imas-mcp
```

VS Code:

```json
{
  "servers": {
    "imas-mcp-uv": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--active", "imas-mcp", "--no-rich"]
    }
  }
}
```

Claude Desktop:

```json
{
  "mcpServers": {
    "imas-mcp-uv": {
      "command": "uv",
      "args": ["run", "--active", "imas-mcp", "--no-rich"]
    }
  }
}
```

### Docker Setup

Run locally in a container (pre-built indexes included):

```bash
docker run -d \
  --name imas-mcp \
  -p 8000:8000 \
  ghcr.io/iterorganization/imas-mcp:latest-streamable-http

# Optional: verify
docker ps --filter name=imas-mcp --format "table {{.Names}}\t{{.Status}}"
```

VS Code (`.vscode/mcp.json`):

```json
{
  "servers": {
    "imas-mcp-docker": { "type": "http", "url": "http://localhost:8000/mcp" }
  }
}
```

Claude Desktop:

```json
{
  "mcpServers": {
    "imas-mcp-docker": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

### Slurm / HPC (STDIO)

Helper script: `scripts/imas_mcp_slurm_stdio.sh`

VS Code (`.vscode/mcp.json`, JSONC ok):

```jsonc
{
  "servers": {
    "imas-slurm-stdio": {
      "type": "stdio",
      "command": "scripts/imas_mcp_slurm_stdio.sh"
    }
  }
}
```

Launch behavior:

1. If `SLURM_JOB_ID` present → start inside current allocation.
2. Else requests node with `srun --pty` then starts server (unbuffered stdio).

Resource tuning (export before client starts):

| Variable                   | Purpose                                  | Default         |
| -------------------------- | ---------------------------------------- | --------------- |
| `IMAS_MCP_SLURM_TIME`      | Walltime                                 | `08:00:00`      |
| `IMAS_MCP_SLURM_CPUS`      | CPUs per task                            | `1`             |
| `IMAS_MCP_SLURM_MEM`       | Memory (e.g. `4G`)                       | Slurm default   |
| `IMAS_MCP_SLURM_PARTITION` | Partition                                | Cluster default |
| `IMAS_MCP_SLURM_ACCOUNT`   | Account/project                          | User default    |
| `IMAS_MCP_SLURM_EXTRA`     | Extra raw `srun` flags                   | (empty)         |
| `IMAS_MCP_USE_ENTRYPOINT`  | Use `imas-mcp` entrypoint vs `python -m` | `0`             |

Example:

```bash
export IMAS_MCP_SLURM_TIME=02:00:00
export IMAS_MCP_SLURM_CPUS=4
export IMAS_MCP_SLURM_MEM=8G
export IMAS_MCP_SLURM_PARTITION=compute
```

Direct CLI:

```bash
scripts/imas_mcp_slurm_stdio.sh --ids-filter "core_profiles equilibrium"
```

Why STDIO? Avoids opening network ports; all traffic rides the existing `srun` pseudo-TTY.

---

## Example IMAS Queries

Once you have the IMAS MCP server configured, you can interact with it using natural language queries. Use the `@imas` prefix to direct queries to the IMAS server:

### Basic Search Examples

```text
@imas Find data paths related to plasma temperature
@imas Search for electron density measurements
@imas What data is available for magnetic field analysis?
@imas Show me core plasma profiles
```

### Physics Concept Exploration

```text
@imas Explain what equilibrium reconstruction means in plasma physics
@imas What is the relationship between pressure and magnetic fields?
@imas How do transport coefficients relate to plasma confinement?
@imas Describe the physics behind current drive mechanisms
```

### Data Structure Analysis

```text
@imas Analyze the structure of the core_profiles IDS
@imas What are the relationships between equilibrium and core_profiles?
@imas Show me identifier schemas for transport data
@imas Export bulk data for equilibrium, core_profiles, and transport IDS
```

### Advanced Queries

```text
@imas Find all paths containing temperature measurements across different IDS
@imas What physics domains are covered in the IMAS data dictionary?
@imas Show me measurement dependencies for fusion power calculations
@imas Explore cross-domain relationships between heating and confinement
```

### Workflow and Integration

```text
@imas How do I access electron temperature profiles from IMAS data?
@imas What's the recommended workflow for equilibrium analysis?
@imas Show me the branching logic for diagnostic identifier schemas
@imas Export physics domain data for comprehensive transport analysis
```

The IMAS MCP server provides 8 specialized tools for different types of queries:

- **Search**: Natural language and structured search across IMAS data paths
- **Explain**: Physics concepts with IMAS context and domain expertise
- **Overview**: General information about IMAS structure and available data
- **Analyze**: Detailed structural analysis of specific IDS
- **Explore**: Relationship discovery between data paths and physics domains
- **Identifiers**: Exploration of enumerated options and branching logic
- **Bulk Export**: Comprehensive export of multiple IDS with relationships
- **Domain Export**: Physics domain-specific data with measurement dependencies

## Development

For local development and customization:

### Setup

```bash
# Clone repository
git clone https://github.com/iterorganization/imas-mcp.git
cd imas-mcp

# Install development dependencies (search index build takes ~8 minutes first time)
uv sync --all-extras
```

### Build Dependencies

This project requires additional dependencies during the build process that are not part of the runtime dependencies:

- **`imas-data-dictionary`** - Git development package, required only during wheel building for parsing latest DD changes
- **`rich`** - Used for enhanced console output during build processes

**For runtime:** The `imas-data-dictionaries` PyPI package is now a core dependency and provides access to stable DD versions (e.g., 4.0.0). This eliminates the need for the git package at runtime and ensures reproducible builds.

**For developers:** Build-time dependencies are included in the `[build-system.requires]` section for wheel building. The git package is only needed when building wheels with latest DD changes.

```bash
# Regular development - uses imas-data-dictionaries (PyPI)
uv sync --all-extras

# Set DD version for building (defaults to 4.0.0)
export IMAS_DD_VERSION=4.0.0
uv run build-schemas
```

**Location in configuration:**

- **Build-time dependencies**: Listed in `[build-system.requires]` in `pyproject.toml`
- **Runtime dependencies**: `imas-data-dictionaries>=4.0.0` in `[project.dependencies]`

**Note:** The `IMAS_DD_VERSION` environment variable controls which DD version is used for building schemas and embeddings. Docker containers have this set to `4.0.0` by default.

### Development Commands

```bash
# Run tests
uv run pytest

# Run linting and formatting
uv run ruff check .
uv run ruff format .

# Build schema data structures from IMAS data dictionary
uv run build-schemas

# Build document store and semantic search embeddings
uv run build-embeddings

# Run the server locally (default: streamable-http on port 8000)
uv run --active imas-mcp --no-rich

# Run with stdio transport for MCP clients
uv run --active imas-mcp --no-rich --transport stdio
```

### Build Scripts

The project includes two separate build scripts for creating the required data structures:

**`build-schemas`** - Creates schema data structures from IMAS XML data dictionary:

- Transforms XML data into optimized JSON format
- Creates catalog and relationship files
- Use `--ids-filter "core_profiles equilibrium"` to build specific IDS
- Use `--force` to rebuild even if files exist

**`build-embeddings`** - Creates document store and semantic search embeddings:

- Builds in-memory document store from JSON data
- Generates sentence transformer embeddings for semantic search
- Caches embeddings for fast loading
- Use `--model-name "all-mpnet-base-v2"` for different models
- Use `--force` to rebuild embeddings cache
- Use `--no-normalize` to disable embedding normalization
- Use `--half-precision` to reduce memory usage
- Use `--similarity-threshold 0.1` to set similarity score thresholds

**Note:** The build hook creates JSON data. Build embeddings separately using `build-embeddings` for better control and performance.

### Local Development MCP Configuration

#### VS Code

The repository includes a `.vscode/mcp.json` file with pre-configured development server options. Use the `imas-local-stdio` configuration for local development.

#### Claude Desktop

Add to your config file:

```json
{
  "mcpServers": {
    "imas-local-dev": {
      "command": "uv",
      "args": ["run", "--active", "imas-mcp", "--no-rich", "--auto-build"],
      "cwd": "/path/to/imas-mcp"
    }
  }
}
```

## How It Works

1. **Installation**: During package installation, the index builds automatically when the module first imports
2. **Build Process**: The system parses the IMAS data dictionary and creates comprehensive JSON files with structured data
3. **Embedding Generation**: Creates semantic embeddings using sentence transformers for advanced search capabilities
4. **Serialization**: The system stores indexes in organized subdirectories:
   - **JSON data**: `imas_mcp/resources/schemas/` (LLM-optimized structured data)
   - **Embeddings cache**: Pre-computed sentence transformer embeddings for semantic search
5. **Import**: When importing the module, the pre-built index and embeddings load in ~1 second

## Optional Dependencies and Runtime Requirements

The IMAS MCP server now includes `imas-data-dictionaries` as a core dependency, providing stable DD version access (default: 4.0.0). The git development package (`imas-data-dictionary`) is used during wheel building when parsing latest DD changes.

### Package Installation Options

- **Runtime**: `uv add imas-mcp` - Includes all transports (stdio, sse, streamable-http)
- **Full installation**: `uv add imas-mcp` - Recommended for all users

### Data Dictionary Access

The system uses composable accessors to access IMAS Data Dictionary version and metadata:

1. **Environment Variable**: `IMAS_DD_VERSION` (highest priority) - Set to specify DD version (e.g., "4.0.0")
2. **Metadata File**: JSON metadata stored alongside indexes
3. **Index Name Parsing**: Extracts version from index filename
4. **Package Default**: Falls back to `imas-data-dictionaries` package (4.0.0)

This design ensures the server can:

- **Build indexes** using the version specified by `IMAS_DD_VERSION`
- **Run with pre-built indexes** using version metadata
- **Access stable DD versions** through `imas-data-dictionaries` PyPI package

### Index Building vs Runtime

- **Index Building**: Requires `imas-data-dictionary` package to parse XML and create indexes
- **Runtime Search**: Only requires pre-built indexes and metadata, no IMAS package dependency
- **Version Access**: Uses composable accessor pattern with multiple fallback strategies

## Implementation Details

### Search Implementation

The search system is the core component that provides fast, flexible search capabilities over the IMAS Data Dictionary. It combines efficient indexing with IMAS-specific data processing and semantic search to enable different search modes:

#### Search Methods

1. **Semantic Search** (`SearchMode.SEMANTIC`):

   - AI-powered semantic understanding using sentence transformers
   - Natural language queries with physics context awareness
   - Finds conceptually related terms even without exact keyword matches
   - Best for exploratory research and concept discovery

2. **Lexical Search** (`SearchMode.LEXICAL`):

   - Fast text-based search with exact keyword matching
   - Boolean operators (`AND`, `OR`, `NOT`)
   - Wildcards (`*` and `?` patterns)
   - Field-specific searches (e.g., `documentation:plasma ids:core_profiles`)
   - Fastest performance for known terminology

3. **Hybrid Search** (`SearchMode.HYBRID`):

   - Combines semantic and lexical approaches
   - Provides both exact matches and conceptual relevance
   - Balanced performance and comprehensiveness

4. **Auto Search** (`SearchMode.AUTO`):
   - Intelligent search mode selection based on query characteristics
   - Automatically chooses optimal search strategy
   - Adaptive performance optimization

#### Key Capabilities

- **Search Mode Selection**: Choose between semantic, lexical, hybrid, or auto modes
- **Performance Caching**: TTL-based caching system with hit rate monitoring
- **Semantic Embeddings**: Pre-computed sentence transformer embeddings for fast semantic search
- **Physics Context**: Domain-aware search with IMAS-specific terminology
- **Advanced Query Parsing**: Supports complex search expressions and field filtering
- **Relevance Ranking**: Results sorted by match quality and physics relevance

## Future Work

### MCP Resources Implementation (Phase 2 - Planned)

We plan to implement MCP resources to provide efficient access to pre-computed IMAS data:

#### Planned Resource Features

- **Static JSON IDS Data**: Pre-computed IDS catalog and structure data served as MCP resources
- **Physics Measurement Data**: Domain-specific measurement data and relationships
- **Usage Examples**: Code examples and workflow patterns for common analysis tasks
- **Documentation Resources**: Interactive documentation and API references

#### Resource Types

- `ids://catalog` - Complete IDS catalog with metadata
- `ids://structure/{ids_name}` - Detailed structure for specific IDS
- `ids://physics-domains` - Physics domain mappings and relationships
- `examples://search-patterns` - Common search patterns and workflows

### MCP Prompts Implementation (Phase 3 - Planned)

Specialized prompts for physics analysis and workflow automation:

#### Planned Prompt Categories

- **Physics Analysis Prompts**: Specialized prompts for plasma physics analysis tasks
- **Code Generation Prompts**: Generate Python analysis code for IMAS data
- **Workflow Automation Prompts**: Automate complex multi-step analysis workflows
- **Data Validation Prompts**: Create validation approaches for IMAS measurements

#### Prompt Templates

- `physics-explain` - Generate comprehensive physics explanations
- `measurement-workflow` - Create measurement analysis workflows
- `cross-ids-analysis` - Analyze relationships between multiple IDS
- `imas-python-code` - Generate Python code for data analysis

### Performance Optimization (Phase 4 - In Progress)

Continued optimization of search and tool performance:

#### Current Optimizations (Implemented)

- ✅ **Search Mode Selection**: Multiple search modes (semantic, lexical, hybrid, auto)
- ✅ **Search Caching**: TTL-based caching with hit rate monitoring for search operations
- ✅ **Semantic Embeddings**: Pre-computed sentence transformer embeddings
- ✅ **ASV Benchmarking**: Automated performance monitoring and regression detection

#### Planned Optimizations

- **Advanced Caching Strategy**: Intelligent cache management for all MCP operations (beyond search)
- **Performance Monitoring**: Enhanced metrics tracking and analysis across all tools
- **Multi-Format Export**: Optimized export formats (raw, structured, enhanced)
- **Selective AI Enhancement**: Conditional AI enhancement based on request context

### Testing and Quality Assurance (Phase 5 - Planned)

Comprehensive testing strategy for all MCP components:

#### Test Implementation Goals

- **MCP Tool Testing**: Complete test coverage using FastMCP 2 testing framework
- **Resource Testing**: Validation of all MCP resources and data integrity
- **Prompt Testing**: Automated testing of prompt templates and responses
- **Performance Testing**: Benchmarking and regression detection for all tools

## Docker Usage

The server is available as a pre-built Docker container with the index already built:

```bash
# Pull and run the latest container
docker run -d -p 8000:8000 ghcr.io/iterorganization/imas-mcp:latest

# Or use Docker Compose
docker-compose up -d
```

See [DOCKER.md](DOCKER.md) for detailed container usage, deployment options, and troubleshooting.

[python-badge]: https://img.shields.io/badge/python-3.12-blue
[python-link]: https://www.python.org/downloads/
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
[ruff-link]: https://docs.astral.sh/ruff/
[pre-commit-badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-link]: https://github.com/pre-commit/pre-commit
[build-deploy-badge]: https://img.shields.io/github/actions/workflow/status/simon-mcintosh/imas-mcp/test.yml?branch=main&color=brightgreen&label=CI%2FCD
[build-deploy-link]: https://github.com/iterorganization/imas-mcp/actions/workflows/test.yml
[codecov-badge]: https://codecov.io/gh/simon-mcintosh/imas-mcp/graph/badge.svg
[codecov-link]: https://codecov.io/gh/simon-mcintosh/imas-mcp
[docs-badge]: https://img.shields.io/badge/docs-online-brightgreen
[docs-link]: https://simon-mcintosh.github.io/imas-mcp/
[asv-badge]: https://img.shields.io/badge/ASV-Benchmarks-blue?style=flat&logo=speedtest&logoColor=white
[asv-link]: https://simon-mcintosh.github.io/imas-mcp/benchmarks/
