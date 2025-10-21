# qBraid-CLI Development Guide

This document provides a comprehensive overview of the qBraid-CLI project structure, development practices, and workflows to help AI assistants (like Claude) and developers quickly understand and contribute to the project.

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Project Structure](#project-structure)
3. [Development Environment](#development-environment)
4. [Code Style & Linting](#code-style--linting)
5. [Testing Protocol](#testing-protocol)
6. [Documentation](#documentation)
7. [GitHub Workflows](#github-workflows)
8. [CLI Architecture (Typer)](#cli-architecture-typer)
9. [Project Configuration](#project-configuration)
10. [Common Development Tasks](#common-development-tasks)
11. [Best Practices](#best-practices)

---

## Repository Overview

**qBraid-CLI** is a command-line interface for interacting with qBraid cloud services and quantum software management tools. It provides access to:

- **Quantum Jobs**: Submit and manage quantum jobs on various QPUs and simulators
- **Environments**: Manage Python environments and quantum software installations
- **Devices**: Browse and query quantum device catalog
- **Files**: Cloud storage file management
- **Kernels**: Jupyter kernel management
- **Chat**: Interact with qBraid AI chat service
- **MCP**: Model Context Protocol aggregator for Claude Desktop integration

### Key Technologies

- **Python 3.9+**: Minimum supported version
- **Typer**: CLI framework (based on Click)
- **Rich**: Terminal formatting and UI
- **qbraid-core**: Core library for qBraid services
- **pytest**: Testing framework

---

## Project Structure

```
qBraid-CLI/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
│       ├── main.yml        # Primary test/build workflow
│       ├── docs.yml        # Documentation build/deploy
│       ├── format.yml      # Code formatting checks
│       └── ...
├── docs/                   # Sphinx documentation
│   ├── requirements.txt    # Docs dependencies
│   └── tree/              # Generated CLI reference
├── qbraid_cli/            # Main package
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── exceptions.py      # Custom exceptions
│   ├── handlers.py        # Error handlers
│   ├── account/           # Account commands
│   ├── admin/             # Admin/CI commands
│   ├── chat/              # Chat commands
│   ├── configure/         # Configuration commands
│   ├── devices/           # Device commands
│   ├── envs/              # Environment commands
│   ├── files/             # File commands
│   ├── jobs/              # Jobs commands
│   ├── kernels/           # Kernel commands
│   ├── mcp/               # MCP aggregator commands
│   │   ├── __init__.py
│   │   ├── app.py         # Command definitions
│   │   └── serve.py       # MCP server implementation
│   └── pip/               # Pip wrapper commands
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest configuration
│   ├── account/
│   ├── admin/
│   ├── configure/
│   ├── devices/
│   ├── envs/
│   ├── files/
│   ├── jobs/
│   ├── kernels/
│   ├── mcp/               # MCP tests
│   │   ├── test_mcp_list.py
│   │   ├── test_mcp_serve.py
│   │   └── test_mcp_status.py
│   └── resources/
├── tools/                 # Development scripts
│   ├── split_rst.py       # Doc generation helper
│   └── bump_version.py    # Version management
├── pyproject.toml         # Project configuration (central!)
├── CONTRIBUTING.md        # Contribution guidelines
├── MCP_IMPLEMENTATION_PROGRESS.md  # MCP feature documentation
└── CLAUDE.md             # This file
```

### Module Organization

Each command group follows a consistent pattern:

```python
qbraid_cli/<command>/
├── __init__.py           # Exports
├── app.py               # Typer commands (CLI interface)
└── <helpers>.py         # Business logic, validation, etc.
```

**Example** (`qbraid_cli/mcp/`):
- `app.py`: Defines `mcp_app = typer.Typer()` with commands (list, serve, status)
- `serve.py`: Contains `MCPAggregatorServer` class and `serve_mcp()` function

---

## Development Environment

### Installation

```bash
# Clone repository
git clone https://github.com/qBraid/qBraid-CLI.git
cd qBraid-CLI

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Or install specific extras
pip install -e .[dev,envs,jobs,mcp]
```

### Python Environment

- **Minimum**: Python 3.9
- **Recommended**: Python 3.11+ for development
- **Tested on**: 3.9, 3.10, 3.11, 3.12, 3.13

### Key Dependencies

```toml
# Core dependencies (always installed)
typer>=0.12.1
rich>=10.11.0
click<=8.1.8
qbraid-core>=0.1.42,<0.2

# Optional extras
[envs]  -> qbraid-core[environments]
[jobs]  -> amazon-braket-sdk>=1.48.1
[mcp]   -> qbraid-core[mcp]
[dev]   -> isort, black, pytest, pytest-cov, pytest-asyncio
```

---

## Code Style & Linting

### Tools Used

1. **black**: Code formatting (line length: 100)
2. **isort**: Import sorting (black-compatible profile)
3. **pylint**: Code linting (max line length: 100)
4. **mypy**: Static type checking
5. **qbraid admin headers**: Copyright header management

### Configuration

All tool configurations are in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311", "py312"]

[tool.isort]
profile = "black"
line_length = 100

[tool.pylint.'MESSAGES CONTROL']
max-line-length = 100
disable = "C0415, R0914, W0511"
```

### Running Linters

```bash
# Format code
black qbraid_cli tests tools
isort qbraid_cli tests tools

# Check code quality
pylint qbraid_cli tests tools
mypy qbraid_cli tests tools

# Fix copyright headers
qbraid admin headers qbraid_cli tests tools --type=default --fix
```

### Pre-commit Checklist

Before committing, ensure:
1. ✅ All linters pass (black, isort, pylint, mypy)
2. ✅ All tests pass (`pytest tests/`)
3. ✅ Copyright headers are correct
4. ✅ Type hints are present for new functions
5. ✅ Docstrings follow Google style

### Common Linting Issues & Fixes

**Logging with f-strings** ❌:
```python
logger.error(f"Failed to connect: {error}")  # Wrong
```

**Use lazy formatting** ✅:
```python
logger.error("Failed to connect: %s", error)  # Correct
```

**Broad exception catching**:
```python
except Exception as err:  # pylint: disable=broad-exception-caught
    logger.error("Error: %s", err)
```

---

## Testing Protocol

### Test Framework

- **pytest**: Primary test runner
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support (for MCP tests)

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/mcp/test_mcp_list.py

# Run with coverage
pytest --cov=qbraid_cli tests/

# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/mcp/test_mcp_list.py::test_list_servers_success
```

### Test Structure

Tests follow the same structure as the main package:

```
tests/<command>/test_<command>_<action>.py
```

**Example**:
- `tests/mcp/test_mcp_list.py`: Tests for `qbraid mcp list`
- `tests/mcp/test_mcp_serve.py`: Tests for `qbraid mcp serve`

### Writing Tests

**Standard test pattern**:

```python
from unittest.mock import MagicMock, patch
import pytest
import typer
from typer.testing import CliRunner

runner = CliRunner()

def test_command_success(capsys):
    """Test successful command execution."""
    with patch("module.function", return_value="result"):
        command_function(arg="value")
        captured = capsys.readouterr()
        assert "expected output" in captured.out

def test_command_error(capsys):
    """Test error handling."""
    with patch("module.function", side_effect=RuntimeError("error")):
        with pytest.raises(typer.Exit) as exc_info:
            command_function(arg="value")
        assert exc_info.value.exit_code == 1

def test_cli_integration():
    """Test via CLI runner."""
    result = runner.invoke(app, ["command", "--option", "value"])
    assert result.exit_code == 0
    assert "expected" in result.stdout
```

### Async Tests (MCP)

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    mock_client = AsyncMock()
    await function_under_test(mock_client)
    mock_client.connect.assert_called_once()
```

### Test Fixtures

Common fixtures are in `tests/conftest.py`:

```python
@pytest.fixture
def mock_session():
    """Mock QbraidSession."""
    session = MagicMock()
    session.get_user.return_value = {"email": "test@example.com"}
    return session
```

### Coverage Goals

- Aim for >80% coverage on new code
- Critical paths should have 100% coverage
- Edge cases and error handling must be tested

---

## Documentation

### Building Docs Locally

```bash
# Install doc dependencies
pip install -r docs/requirements.txt

# Build docs
make docs

# Or manually
sphinx-build -W -b html docs docs/build/html

# View docs (macOS)
open docs/build/html/index.html
```

### Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst           # Main documentation page
├── tree/               # Auto-generated CLI reference
└── _static/            # Static assets (CSS, images)
```

### Generating CLI Reference

The CLI reference is auto-generated from Typer docstrings:

```bash
# Generate command tree
typer qbraid_cli.main utils docs --name=qbraid --output=docs/tree/qbraid.md

# Convert to RST
m2r docs/tree/qbraid.md
rm docs/tree/qbraid.md

# Split into separate files
python tools/split_rst.py docs/tree/qbraid.rst
```

### Docstring Style

Use **Google style** docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Short description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When input is invalid

    Example:
        >>> function("test", 42)
        True
    """
```

---

## GitHub Workflows

### main.yml (Primary CI/CD)

**Triggers**: Push to main, PRs to main, manual dispatch

**Jobs**:

1. **build** (Python 3.11, Ubuntu)
   - Build wheel package
   - Upload as artifact

2. **test** (Matrix: Python 3.9-3.13, Ubuntu + Windows)
   - Install built wheel
   - Install dev dependencies: `pip install .[dev,envs]`
   - Run pytest with coverage
   - Upload coverage to Codecov (Python 3.11, Ubuntu only)

**Key Feature**: Tests use the **built wheel**, not source code, ensuring distribution works correctly.

### docs.yml

**Triggers**: Push to main

**Purpose**: Build and deploy Sphinx documentation to GitHub Pages or Read the Docs.

### format.yml

**Triggers**: PRs

**Purpose**: Check code formatting with black and isort (non-blocking, informational).

### Other Workflows

- `bump-version.yml`: Automated version bumping
- `publish.yml`: PyPI publishing
- `pre-release.yml`: Pre-release version management
- `tag-on-merge.yml`: Automatic tagging on merge to main

---

## CLI Architecture (Typer)

### Entry Point

The main CLI entry point is in `qbraid_cli/main.py`:

```python
import typer

app = typer.Typer(help="The qBraid CLI.")

# Register command groups
from qbraid_cli.account import account_app
from qbraid_cli.devices import devices_app
from qbraid_cli.mcp import mcp_app

app.add_typer(account_app, name="account")
app.add_typer(devices_app, name="devices")
app.add_typer(mcp_app, name="mcp")

if __name__ == "__main__":
    app()
```

### Command Group Pattern

Each command group is a separate Typer app:

```python
# qbraid_cli/mcp/app.py
import typer

mcp_app = typer.Typer(help="MCP (Model Context Protocol) aggregator commands")

@mcp_app.command("list")
def list_servers(
    workspace: str = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Filter by workspace",
    ),
):
    """
    List available qBraid MCP servers.
    """
    # Implementation
    pass
```

### Command Structure

```
qbraid [GLOBAL_OPTIONS] <group> <command> [OPTIONS] [ARGS]

Examples:
  qbraid mcp list --workspace lab
  qbraid devices list --fmt
  qbraid jobs get JOB_ID --no-fmt
```

### Options vs Arguments

- **Options**: Named parameters (`--option`, `-o`)
- **Arguments**: Positional parameters

```python
@app.command()
def get(
    device_id: str,  # Positional argument (required)
    fmt: bool = typer.Option(True, "--fmt/--no-fmt"),  # Option
):
    pass
```

### Progress Display (Rich)

Use Rich for progress indication:

```python
from rich.console import Console

console = Console()

# Print with color
console.print("[green]Success![/green]")
console.print("[red]Error occurred[/red]")
console.print("[yellow]Warning: ...[/yellow]")

# Tables
from rich.table import Table
table = Table(title="Results")
table.add_column("Name")
table.add_column("Value")
table.add_row("key", "value")
console.print(table)

# Progress bars
from rich.progress import track
for item in track(items, description="Processing..."):
    process(item)
```

### Error Handling

Use `typer.Exit` for clean exits:

```python
import typer

def command():
    if error_condition:
        typer.secho("Error message", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)  # Exit with error code

    typer.secho("Success!", fg=typer.colors.GREEN)
```

---

## Project Configuration

### pyproject.toml (Central Configuration)

**Everything** is configured in `pyproject.toml`:

```toml
[project]
name = "qbraid-cli"
version = "0.10.8"
dependencies = [...]
requires-python = ">= 3.9"

[project.optional-dependencies]
jobs = [...]
envs = [...]
mcp = [...]
dev = ["isort", "black", "pytest", "pytest-cov", "pytest-asyncio"]

[project.scripts]
qbraid = "qbraid_cli.main:app"

[tool.black]
line-length = 100

[tool.isort]
profile = "black"
line_length = 100

[tool.pylint.'MESSAGES CONTROL']
max-line-length = 100
disable = "C0415, R0914, W0511"

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = ["tests"]

[tool.coverage.run]
source = ["qbraid_cli"]

[tool.coverage.report]
show_missing = true
skip_covered = true
```

### Version Management

Version is defined in `pyproject.toml`:

```toml
[project]
version = "0.10.8"

[tool.setuptools_scm]
write_to = "qbraid_cli/_version.py"
```

The `_version.py` file is auto-generated during build. **Do not edit manually**.

---

## Common Development Tasks

### Adding a New Command Group

1. **Create module structure**:
   ```bash
   mkdir qbraid_cli/newgroup
   touch qbraid_cli/newgroup/{__init__.py,app.py}
   ```

2. **Define commands** in `app.py`:
   ```python
   import typer

   newgroup_app = typer.Typer(help="New group commands")

   @newgroup_app.command("action")
   def action_command():
       """Perform action."""
       pass
   ```

3. **Register in main.py**:
   ```python
   from qbraid_cli.newgroup import newgroup_app
   app.add_typer(newgroup_app, name="newgroup")
   ```

4. **Create tests**:
   ```bash
   mkdir tests/newgroup
   touch tests/newgroup/{__init__.py,test_newgroup_action.py}
   ```

5. **Add copyright headers**:
   ```bash
   qbraid admin headers qbraid_cli/newgroup tests/newgroup --type=default --fix
   ```

6. **Update documentation index** - Add to `docs/index.rst`:
   ```rst
   .. toctree::
      :maxdepth: 1
      :caption: CLI API Reference
      :hidden:

      tree/qbraid
      tree/qbraid_admin
      tree/qbraid_configure
      tree/qbraid_account
      tree/qbraid_chat
      tree/qbraid_devices
      tree/qbraid_envs
      tree/qbraid_files
      tree/qbraid_jobs
      tree/qbraid_kernels
      tree/qbraid_mcp
      tree/qbraid_newgroup  # <-- Add your new group here (alphabetical order)
      tree/qbraid_pip
   ```

7. **Update README.md** - Add to the Commands list in the help output example:
   ```markdown
   Commands
     account                       Manage qBraid account
     ...
     newgroup                      New group commands description.
     ...
   ```

8. **Run linters and tests**:
   ```bash
   black qbraid_cli/newgroup tests/newgroup
   isort qbraid_cli/newgroup tests/newgroup
   pytest tests/newgroup/ -v
   ```

9. **Build docs to verify**:
   ```bash
   make docs
   ```

### Adding Tests

1. **Create test file**: `tests/<group>/test_<group>_<action>.py`

2. **Add copyright header**:
   ```python
   # Copyright (c) 2025, qBraid Development Team
   # All rights reserved.

   """
   Unit tests for <description>.
   """
   ```

3. **Write tests** with descriptive names:
   ```python
   def test_command_success():
       """Test successful execution."""
       pass

   def test_command_error_handling():
       """Test error handling."""
       pass

   def test_command_cli_integration():
       """Test via CLI."""
       pass
   ```

4. **Run tests**:
   ```bash
   pytest tests/<group>/ -v
   ```

### Updating Dependencies

1. **Update `pyproject.toml`**:
   ```toml
   [project.optional-dependencies]
   dev = ["isort", "black", "pytest", "pytest-cov", "pytest-asyncio", "new-dep"]
   ```

2. **No need to update GitHub workflows** - they use `pip install .[dev,envs]`

3. **Update `CONTRIBUTING.md`** if needed

4. **Test locally**:
   ```bash
   pip install -e .[dev]
   pytest tests/
   ```

### Building & Publishing

```bash
# Build package
python -m build

# Check distribution
twine check dist/*

# Test upload (TestPyPI)
twine upload --repository testpypi dist/*

# Production upload (requires credentials)
twine upload dist/*
```

---

## Best Practices

### Code Organization

1. **Separate concerns**: CLI logic in `app.py`, business logic in separate modules
2. **Avoid circular imports**: Use lazy imports if needed
3. **Keep functions focused**: Single responsibility principle
4. **Use type hints**: Always include type hints for function signatures

### Error Handling

1. **Use specific exceptions**: Don't catch bare `Exception` unless necessary
2. **Provide helpful messages**: Include context in error messages
3. **Log appropriately**: Use `logging` module, not `print()`
4. **Exit cleanly**: Use `typer.Exit(code)` instead of `sys.exit()`

### Testing

1. **Test at multiple levels**: Unit tests, integration tests, CLI tests
2. **Mock external dependencies**: Don't make real API calls in tests
3. **Use fixtures**: Reuse common setup code
4. **Name tests descriptively**: `test_<function>_<condition>_<expected_result>`

### Documentation

1. **Docstrings for public APIs**: All public functions and classes
2. **Update CONTRIBUTING.md**: Keep development instructions current
3. **Comment complex logic**: Explain "why", not "what"
4. **Keep CLAUDE.md updated**: Add new patterns and practices

### Git Workflow

1. **Branch naming**: `feature/<name>`, `bugfix/<name>`, `docs/<name>`
2. **Commit messages**: Clear, concise, imperative mood
3. **Small PRs**: Easier to review, faster to merge
4. **Run tests locally**: Before pushing

### Performance

1. **Lazy imports**: Import heavy dependencies only when needed
2. **Cache results**: Use `@functools.lru_cache` for expensive operations
3. **Async where appropriate**: For I/O-bound operations (like MCP)

---

## Quick Reference

### File Locations

| File | Purpose |
|------|---------|
| `pyproject.toml` | **Central config** - dependencies, tools, metadata |
| `qbraid_cli/main.py` | CLI entry point, command registration |
| `qbraid_cli/<group>/app.py` | Command definitions for each group |
| `tests/<group>/test_*.py` | Tests for each command group |
| `.github/workflows/main.yml` | Primary CI/CD workflow |
| `CONTRIBUTING.md` | Developer setup and guidelines |
| `CLAUDE.md` | This file - comprehensive dev guide |

### Commands Cheat Sheet

```bash
# Development
pip install -e .[dev,envs,mcp]

# Linting
black qbraid_cli tests tools
isort qbraid_cli tests tools
pylint qbraid_cli tests tools
mypy qbraid_cli tests tools
qbraid admin headers qbraid_cli tests tools --type=default --fix

# Testing
pytest tests/ -v
pytest tests/mcp/ -v
pytest --cov=qbraid_cli tests/

# Docs
make docs
open docs/build/html/index.html

# Build
python -m build

# Run CLI without installing
python -m qbraid_cli.main [OPTIONS] COMMAND [ARGS]
```

---

## MCP-Specific Notes

The MCP (Model Context Protocol) implementation is a key feature:

- **Location**: `qbraid_cli/mcp/`
- **Tests**: `tests/mcp/` (31 tests, 100% passing)
- **Purpose**: Aggregates multiple qBraid MCP servers for Claude Desktop
- **Architecture**: Async stdio server with WebSocket backend connections
- **Key files**:
  - `app.py`: CLI commands (list, serve, status)
  - `serve.py`: `MCPAggregatorServer` class
- **Dependencies**: Requires `qbraid-core[mcp]` which includes `websockets`
- **Testing**: Uses `pytest-asyncio` for async test support

See `MCP_IMPLEMENTATION_PROGRESS.md` for detailed implementation notes.

---

## Additional Resources

- **qBraid Docs**: https://docs.qbraid.com/cli/
- **Typer Docs**: https://typer.tiangolo.com/
- **Rich Docs**: https://rich.readthedocs.io/
- **pytest Docs**: https://docs.pytest.org/
- **MCP Protocol**: https://modelcontextprotocol.io/

---

**Last Updated**: October 17, 2025

*This document should be updated whenever significant changes are made to project structure, workflows, or development practices.*
