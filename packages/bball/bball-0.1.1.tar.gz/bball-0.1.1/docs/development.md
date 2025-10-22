# bball Development Guide

Complete guide for developers working on the bball ecosystem.

## Table of Contents

- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Development Setup](#development-setup)
- [Workspace Configuration](#workspace-configuration)
- [Development Workflow](#development-workflow)
- [Tool Configuration](#tool-configuration)
- [Testing Strategy](#testing-strategy)
- [Publishing to PyPI](#publishing-to-pypi)

## Architecture

### Package Design

The bball ecosystem uses a monorepo structure with a main package and optional extension packages:

```
bball (root package - core functionality)
├── bball-cli (optional - command-line interface)
├── bball-api (optional - REST/GraphQL API server)
├── bball-data (optional - data fetching and processing)
├── bball-strategies (optional - analysis strategies)
└── bball-reports (optional - report generation)
```

### Installation Patterns

Users can install exactly what they need:

```bash
# Just core functionality
pip install bball

# Core + specific components
pip install bball[cli]
pip install bball[analytics]  # data, strategies, reports

# Everything
pip install bball[all]
```

### Design Decisions

**Why root package contains core code?**
- Standard pattern used by Django, FastAPI, Requests, etc.
- Clear mental model: repository name = main package name
- Simpler paths and more intuitive development

**Why workspace structure?**
- Single lock file ensures version consistency across all packages
- Editable installs: changes in one package immediately available to others
- Efficient development: no need to reinstall when making changes
- Simplified CI/CD: one repository, one test suite

**Why separate packages?**
- Clear dependencies: each package only depends on what it needs
- Optional features: users don't install heavy dependencies they won't use
- Independent updates: packages can be updated without touching others

## Repository Structure

```
bball/                              # Repository root
├── .python-version                 # Python 3.13
├── pyproject.toml                  # Root package (bball) + workspace config
├── uv.lock                         # Shared dependency lock file
├── README.md                       # User-facing documentation
├── LICENSE                         # MIT License
│
├── src/                           # Main bball package code
│   └── bball/
│       ├── __init__.py           # Package exports
│       ├── models.py             # Player, Team, Game, Stats models
│       └── utils.py              # Utility functions
│
├── docs/                         # Documentation
│   └── development.md           # This file
│
└── packages/                     # Optional extension packages
    ├── bball-cli/               # CLI application
    │   ├── pyproject.toml
    │   ├── README.md
    │   └── src/bball_cli/
    │       ├── __init__.py
    │       └── main.py
    │
    ├── bball-api/               # API server
    │   ├── pyproject.toml
    │   ├── README.md
    │   └── src/bball_api/
    │       └── __init__.py
    │
    ├── bball-data/              # Data processing
    │   ├── pyproject.toml
    │   ├── README.md
    │   └── src/bball_data/
    │       └── __init__.py
    │
    ├── bball-strategies/        # Analysis strategies
    │   ├── pyproject.toml
    │   ├── README.md
    │   └── src/bball_strategies/
    │       └── __init__.py
    │
    └── bball-reports/           # Report generation
        ├── pyproject.toml
        ├── README.md
        └── src/bball_reports/
            └── __init__.py
```

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) - Modern Python package manager

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/bball-dev/bball.git
cd bball

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all workspace packages in development mode
# This will automatically install Python 3.13 if not present
uv sync --all-packages

# Verify installation
uv run python --version  # Should show Python 3.13.x
uv run python -c "from bball import Player; print('Installation successful!')"
```

### What `uv sync --all-packages` Does

1. Reads `.python-version` file (pins to Python 3.13)
2. Downloads and installs Python 3.13 if not present
3. Creates `.venv` virtual environment
4. Installs all workspace packages in editable mode
5. Installs all development dependencies (pytest, ruff, pyright, etc.)
6. Creates/updates `uv.lock` file with pinned dependencies

## Workspace Configuration

### How uv Workspaces Work

The root `pyproject.toml` serves two roles:

1. **Package Definition** - Defines the main `bball` package
2. **Workspace Coordinator** - Manages all packages in `packages/`

```toml
# Root pyproject.toml
[project]
name = "bball"  # This is the main package
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["pydantic>=2.9", "numpy>=1.26", ...]

[project.optional-dependencies]
cli = ["bball-cli>=0.1.0"]
api = ["bball-api>=0.1.0"]
# ... etc

[tool.uv.workspace]
members = ["packages/*"]  # All packages in packages/

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "ruff>=0.8",
    "pyright>=1.1",
]
```

### Python Version Management

The repository uses **Python 3.13** exclusively:

- `.python-version`: Contains `3.13` (uv reads this first)
- `pyproject.toml`: `requires-python = ">=3.13"` (allows 3.14+ in future)
- All package files: `requires-python = ">=3.13"`

### Package Dependencies

Each package in `packages/` references the root package via workspace sources:

```toml
# packages/bball-cli/pyproject.toml
[project]
dependencies = ["bball>=0.1.0"]

[tool.uv.sources]
bball = { workspace = true }  # Points to root package
```

During development, this creates editable installs. When publishing to PyPI, these become normal package dependencies.

## Development Workflow

### Common Commands

```bash
# Install/update all packages
uv sync --all-packages

# Install just the root package
uv sync

# Add a dependency to the root package
uv add requests

# Add a dependency to a specific package
uv add --package bball-cli typer

# Add a dev dependency
uv add --dev pytest-asyncio

# Run Python with the venv
uv run python -c "from bball import Player"

# Run a specific package command
uv run bball --help  # If CLI is set up
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests for a specific package
uv run pytest packages/bball-cli/tests/

# Run with coverage
uv run pytest --cov=src --cov=packages --cov-report=term-missing

# Run specific test
uv run pytest packages/bball-data/tests/test_fetch.py::test_player_stats
```

### Code Quality

```bash
# Linting and formatting
uv run ruff check src/ packages/
uv run ruff format src/ packages/

# Type checking
uv run pyright src/ packages/

# Run all quality checks
uv run ruff check src/ packages/ && \
uv run ruff format src/ packages/ && \
uv run pyright src/ packages/ && \
uv run pytest
```

### Building Packages

```bash
# Build root package
uv build

# Build a specific package
uv build --package bball-cli

# Build all packages (manual loop required)
for pkg in packages/*; do
    uv build --package $(basename $pkg)
done
```

### Working on a Specific Package

```bash
# Make changes to packages/bball-data/src/bball_data/fetch.py
# Changes are immediately available to other packages (editable install)

# Test your changes
uv run python -c "from bball_data import fetch_player_stats"

# Run package-specific tests
uv run pytest packages/bball-data/tests/
```

## Tool Configuration

### Configuration Inheritance

Tool configurations are centralized in the root `pyproject.toml` and inherited by all packages.

#### Ruff (Linting/Formatting)

Ruff automatically searches up the directory tree for configuration.

**Root configuration:**
```toml
[tool.ruff]
line-length = 120
target-version = "py313"
src = ["src", "packages"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
```

**Package files:** No `[tool.ruff]` section needed - they inherit from root.

**To override in a package (optional):**
```toml
# packages/bball-cli/pyproject.toml
[tool.ruff]
extend = "../../pyproject.toml"
line-length = 100  # Override just this setting
```

#### Pyright (Type Checking)

**Root configuration:**
```toml
[tool.pyright]
include = ["src", "packages"]
pythonVersion = "3.13"
typeCheckingMode = "standard"
```

#### Pytest (Testing)

**Root configuration:**
```toml
[tool.pytest.ini_options]
testpaths = ["packages/*/tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
]
```

**Best practice:** Always run pytest from the root directory to use root configuration.

#### Coverage

```toml
[tool.coverage.run]
source = ["src", "packages"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```

### Running Tools

Always run tools from the root directory to ensure they use the root configuration:

```bash
# Correct (from root)
uv run ruff check src/ packages/
uv run pyright src/ packages/
uv run pytest

# Avoid (from package directory)
cd packages/bball-cli
uv run ruff check .  # May not use root config correctly
```

## Testing Strategy

### Unit Tests

Each package has its own tests in `packages/*/tests/`:

```
packages/bball-data/
├── src/
│   └── bball_data/
│       └── fetch.py
└── tests/
    ├── __init__.py
    └── test_fetch.py
```

### Integration Tests

Test package interactions:

```python
# tests/integration/test_cli_with_data.py
def test_cli_uses_data_package():
    """Test that CLI can use bball-data when installed."""
    from bball_cli import commands
    from bball_data import fetch_player_stats
    # Test integration
```

### Test Organization

```bash
packages/
├── bball-cli/tests/           # CLI-specific tests
├── bball-api/tests/           # API-specific tests
└── bball-data/tests/          # Data-specific tests

# Optional: integration tests at root
tests/
└── integration/
    ├── test_cli_data.py
    └── test_api_strategies.py
```

## Publishing to PyPI

### Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Create test account at https://test.pypi.org/account/register/
   - Enable 2FA (required)

2. **API Tokens**
   - Generate at https://pypi.org/manage/account/token/
   - Save securely (starts with `pypi-`)
   - Create tokens for both PyPI and Test PyPI

3. **Install Tools**
   ```bash
   uv add --dev build twine
   ```

### Publishing Order

**Critical:** Packages must be published in dependency order!

1. `bball` (root) - No dependencies on other bball packages
2. `bball-cli`, `bball-api`, `bball-data`, `bball-strategies`, `bball-reports` - All depend on `bball`

### Build All Packages

```bash
#!/bin/bash
# build_all.sh

set -e

# Build root package
echo "Building bball (root)..."
uv build

# Build extension packages
PACKAGES=(
    "bball-cli"
    "bball-api"
    "bball-data"
    "bball-strategies"
    "bball-reports"
)

for package in "${PACKAGES[@]}"; do
    echo "Building $package..."
    uv build --package $package
done

echo "All packages built successfully!"
```

### Test with Test PyPI First

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*
twine upload --repository testpypi packages/bball-cli/dist/*
# ... etc

# Test installation
python -m venv test-env
source test-env/bin/activate
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    bball[all]

# Verify it works
bball info
python -c "from bball import Player; print('Success!')"
```

### Publish to Production PyPI

```bash
#!/bin/bash
# publish.sh

set -e

echo "Publishing to PyPI..."

# Root package first
echo "Publishing bball..."
twine upload dist/*
sleep 10  # Wait for PyPI to process

# Extension packages
PACKAGES=(
    "bball-cli"
    "bball-api"
    "bball-data"
    "bball-strategies"
    "bball-reports"
)

for package in "${PACKAGES[@]}"; do
    echo "Publishing $package..."
    twine upload packages/$package/dist/*
    sleep 10
done

echo "All packages published!"
```

### Version Management

```bash
# Update version in root pyproject.toml
# Then update each package's pyproject.toml

# Tag the release
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# Create GitHub release
gh release create v0.2.0 \
    --title "bball v0.2.0" \
    --notes "Release notes here"
```

### Automated Publishing with GitHub Actions

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For PyPI trusted publishing

    steps:
    - uses: actions/checkout@v4

    - uses: astral-sh/setup-uv@v5
      with:
        enable-cache: true

    - name: Build all packages
      run: |
        uv build
        for pkg in packages/*; do
          uv build --package $(basename $pkg)
        done

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        packages-dir: dist/

    # Repeat for each package in packages/
```

## Common Patterns

### Adding a New Package

```bash
# 1. Create package structure
mkdir -p packages/bball-newpkg/src/bball_newpkg

# 2. Create pyproject.toml
cat > packages/bball-newpkg/pyproject.toml << 'EOF'
[project]
name = "bball-newpkg"
version = "0.1.0"
dependencies = ["bball>=0.1.0"]

[tool.uv.sources]
bball = { workspace = true }

[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/bball_newpkg"]
EOF

# 3. Add to root optional dependencies
# Edit root pyproject.toml:
# [project.optional-dependencies]
# newpkg = ["bball-newpkg>=0.1.0"]

# 4. Update workspace
uv sync --all-packages
```

### Smart Optional Imports

```python
# In any package that wants to optionally use another
try:
    from bball_data import fetch_player_stats
    HAS_DATA = True
except ImportError:
    HAS_DATA = False

if HAS_DATA:
    # Use the feature
    data = fetch_player_stats()
else:
    # Provide alternative or inform user
    print("Install bball[data] for data fetching features")
```

### Importing Between Packages

```python
# Always works (bball is a dependency of all packages)
from bball import Player, Team, Game, Stats
from bball import calculate_advanced_stats

# Between optional packages (may not be installed)
try:
    from bball_strategies import analyze_performance
except ImportError:
    # Handle gracefully
    pass
```

## Best Practices

### Code Organization

- Keep the root `bball` package focused on core models and utilities
- Extension packages should be independent and optional
- Avoid circular dependencies between extension packages

### Dependencies

- Root package: Only essential dependencies (pydantic, numpy, pandas, httpx)
- Extension packages: Add specific dependencies as needed
- Use version ranges: `"pydantic>=2.9,<3.0"`

### Testing

- Write tests for all public APIs
- Use fixtures for common test data
- Test optional integrations when available
- Aim for >80% coverage

### Documentation

- Keep README.md user-focused (installation, quick start)
- Document all public functions with Google-style docstrings
- Update this guide when adding new patterns or workflows

### Git Workflow

```bash
# Feature branches
git checkout -b feature/new-analysis-strategy
# Make changes
git add .
git commit -m "Add momentum analysis strategy"
git push origin feature/new-analysis-strategy
# Create PR

# Release workflow
# 1. Update version numbers
# 2. Update CHANGELOG
# 3. Create tag
# 4. Push tag
# 5. GitHub Actions publishes automatically
```

## Troubleshooting

### uv sync fails

```bash
# Clear cache and retry
rm -rf .venv
rm uv.lock
uv sync --all-packages
```

### Import errors during development

```bash
# Ensure all packages are installed in editable mode
uv sync --all-packages

# Check package is installed
uv pip list | grep bball
```

### Type checking errors

```bash
# Ensure pyright uses the workspace Python
uv run pyright src/ packages/

# Check Python version
uv run python --version  # Should be 3.13.x
```

### Build failures

```bash
# Ensure hatchling is available
uv add --dev hatchling

# Clean build artifacts
rm -rf dist/ build/ *.egg-info
uv build
```

## Getting Help

- Documentation: https://docs.bball.dev
- Repository: https://github.com/bball-dev/bball
- Issues: https://github.com/bball-dev/bball/issues
- uv docs: https://docs.astral.sh/uv/
- Python Packaging: https://packaging.python.org/
