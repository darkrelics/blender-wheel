# Tests

This directory contains the test suite for the blender-wheel project.

## Running Tests

Install test dependencies:

```bash
pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=blender-demo --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_config.py
```

## Test Structure

- `test_imports.py` - Tests that all demo modules can be imported
- `test_utils_unit.py` - Unit tests for utility functions
- `test_config.py` - Tests for configuration file validity
- `conftest.py` - Pytest fixtures and configuration

## Notes

- Most tests will be skipped if Blender's `bpy` module is not installed
- Configuration tests validate YAML and TOML file syntax
- Import tests verify code structure without requiring full Blender installation
