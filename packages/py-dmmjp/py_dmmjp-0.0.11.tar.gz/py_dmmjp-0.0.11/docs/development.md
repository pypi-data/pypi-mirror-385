# Development and Testing Commands

This file contains useful commands for developing and testing the py-dmm library.

## Installation

### Development Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .

# Install pre-commit hooks
pre-commit install
```

### Production Installation

```bash
pip install py-dmm
```

## Testing Commands

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=py_dmm --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_client.py -v

# Run tests in parallel
pytest -n auto
```

## Code Quality Commands

```bash
# Format code with black
black py_dmm tests examples

# Sort imports with isort
isort py_dmm tests examples

# Check formatting without making changes
black --check py_dmm tests examples
isort --check-only py_dmm tests examples

# Type checking with mypy
mypy py_dmm

# Linting with pylint
pylint py_dmm

# Run all pre-commit hooks
pre-commit run --all-files
```

## Build and Publish Commands

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Environment Variables

Set up your environment:

```bash
# For development and testing
export DMM_API_KEY="your_dmm_api_key_here"

# For publishing to PyPI
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="your_pypi_token"
```

## Using Makefile

If you prefer using make commands:

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Check formatting
make format-check

# Type checking
make type-check

# Linting
make lint

# Run all quality checks
make quality

# Clean build artifacts
make clean

# Build package
make build

# Upload to Test PyPI
make upload-test

# Upload to PyPI
make upload
```
