# uncertainAPI

A Python package for uncertainAPI.

## Installation

### From PyPI

```bash
pip install uncertainAPI
```

### From source

```bash
git clone https://github.com/Lux-speed-labs/uncertainAPI.git
cd uncertainAPI
make install-dev
```

## Development Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management and Make for task automation.

### Prerequisites

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -
```

### Quick Start

```bash
# Install dependencies and create virtual environment
make install-dev

# Run tests
make test

# Format code
make format

# Run linter
make lint

# Type check
make type-check

# See all available commands
make help
```

## Available Make Commands

### Setup
- `make install` - Install package and create virtual environment
- `make install-dev` - Install with development dependencies

### Development
- `make shell` - Activate virtual environment shell
- `make run` - Run the main application
- `make test` - Run tests
- `make test-cov` - Run tests with coverage report
- `make lint` - Run linter (ruff)
- `make format` - Format code with black
- `make type-check` - Run type checker (mypy)

### Build & Publish
- `make build` - Build distribution packages
- `make publish` - Publish to PyPI

### Cleanup
- `make clean` - Remove build artifacts and cache files

## Usage

```python
import uncertainAPI

# Your code here
```

## Adding Dependencies

```bash
# Add a runtime dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name
```

## Manual Poetry Commands

If you prefer to use Poetry directly:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run command in virtual environment
poetry run python script.py
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
