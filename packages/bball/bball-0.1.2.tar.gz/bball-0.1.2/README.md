# bball

Comprehensive NBA analytics platform for Python.

## Features

- **Core Models** - Pydantic models for Players, Teams, Games, and Stats
- **Advanced Analytics** - Calculate true shooting %, PER, win shares, and more
- **Data Fetching** - Integration with NBA stats API
- **CLI Tools** - Command-line interface for quick analysis
- **API Server** - REST and GraphQL endpoints for your applications
- **Reporting** - Generate visualizations and reports
- **Type Safe** - Full type hints and runtime validation

## Installation

```bash
# Install everything
pip install bball[all]

# Or install specific components
pip install bball              # Just core models and utilities
pip install bball[cli]         # Core + CLI
pip install bball[analytics]   # Core + data, strategies, reports
pip install bball[api]         # Core + API server
```

## Quick Start

```python
from bball import Player, Team, Game, Stats

# Create a player
player = Player(
    id="203999",
    name="Nikola Jokic",
    team_id="DEN",
    position="C",
    height=83,
    weight=284,
    jersey_number=15
)

# Work with stats
from bball import calculate_advanced_stats

stats = Stats(
    points=25.0,
    rebounds=12.0,
    assists=9.0,
    field_goals_made=10,
    field_goals_attempted=18,
    # ... more stats
)

advanced = calculate_advanced_stats(stats)
print(f"True Shooting %: {advanced['true_shooting_pct']:.3f}")
```

## Package Ecosystem

The bball ecosystem consists of a core package and optional extensions:

| Package              | Description                         | Install                         |
| -------------------- | ----------------------------------- | ------------------------------- |
| **bball**            | Core models and utilities           | `pip install bball`             |
| **bball-cli**        | Command-line interface              | `pip install bball[cli]`        |
| **bball-api**        | REST/GraphQL API server             | `pip install bball[api]`        |
| **bball-data**       | Data fetching and processing        | `pip install bball[data]`       |
| **bball-strategies** | Analysis strategies and ML models   | `pip install bball[strategies]` |
| **bball-reports**    | Report generation and visualization | `pip install bball[reports]`    |

## CLI Usage

```bash
# After installing bball[cli]
bball info              # Show installed components
bball version           # Show version information
```

## Development

This project uses modern Python tooling and requires Python 3.13+.

```bash
# Clone the repository
git clone https://github.com/bball-dev/bball.git
cd bball

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all packages in development mode
# This automatically installs Python 3.13 and all dependencies
uv sync --all-packages

# Run tests
uv run pytest

# Run code quality checks
uv run ruff check src/ packages/
uv run ruff format src/ packages/
uv run pyright src/ packages/
```

For detailed development documentation, see [docs/development.md](docs/development.md).

## Documentation

- [Development Guide](docs/development.md) - Complete guide for contributors
- [API Documentation](https://docs.bball.dev) - Full API reference
- [Examples](https://docs.bball.dev/examples) - Usage examples and tutorials

## Contributing

Contributions are welcome! Please see our [development guide](docs/development.md) for:
- Architecture overview
- Development workflow
- Testing strategy
- Publishing process

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`uv run pytest && uv run ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Requirements

- Python 3.13+
- See `pyproject.toml` for package-specific dependencies

## Links

- **Homepage:** https://bball.dev
- **Documentation:** https://docs.bball.dev
- **Repository:** https://github.com/bball-dev/bball
- **Issue Tracker:** https://github.com/bball-dev/bball/issues
- **PyPI:** https://pypi.org/project/bball/

## Credits

Built with:
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [FastAPI](https://fastapi.tiangolo.com/) - API framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
