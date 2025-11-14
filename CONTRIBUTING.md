# Contributing to Blender-Wheel

Thank you for your interest in contributing to blender-wheel! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Commit Guidelines](#commit-guidelines)
8. [Pull Request Process](#pull-request-process)
9. [Reporting Bugs](#reporting-bugs)
10. [Suggesting Enhancements](#suggesting-enhancements)

---

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- Basic understanding of Blender Python API (for demo contributions)
- For build system changes: AWS knowledge or Linux build experience

### Quick Start

```bash
# Clone the repository
git clone https://github.com/darkrelics/blender-wheel.git
cd blender-wheel

# Create a virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/blender-wheel.git
cd blender-wheel

# Add upstream remote
git remote add upstream https://github.com/darkrelics/blender-wheel.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/issue-number-description
```

### 3. Install Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install
```

This will automatically run linting and formatting before each commit.

---

## Making Changes

### Project Structure

```
blender-wheel/
├── .github/workflows/     # CI/CD pipelines
├── cf/                    # CloudFormation templates
├── buildspec.yml/         # AWS CodeBuild specifications
├── blender-demo/          # Demo applications
│   ├── scripts/           # Utility functions
│   └── *.py               # Demo scripts
├── tests/                 # Test suite
├── build_blender_wheel.sh # Local build script
└── docs/                  # Documentation
```

### Areas for Contribution

**Build System**:
- AWS CloudFormation templates (`cf/`)
- Build scripts (`build_blender_wheel.sh`, `buildspec.yml/`)
- Dependency management

**Demo Applications**:
- New demo scripts showing Blender capabilities
- Improvements to utility functions (`blender-demo/scripts/utils.py`)
- Better error handling and user experience

**Testing**:
- Unit tests for utilities
- Integration tests for build process
- Configuration validation tests

**Documentation**:
- Improving README, GETTING_STARTED, LOCAL_BUILD docs
- Adding tutorials or examples
- Fixing typos or clarifications

**CI/CD**:
- GitHub Actions workflows
- Test coverage improvements
- Automated checks

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=blender-demo --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Test Coverage Requirements

- New code should have **at least 70% test coverage**
- Critical functions (build, render, file operations) should have **90%+ coverage**
- All edge cases should be tested

### Writing Tests

**Location**: `tests/` directory

**Naming**:
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

**Example**:

```python
# tests/test_new_feature.py
import pytest
from scripts.utils import your_function

def test_your_function_basic():
    """Test basic functionality."""
    result = your_function(input_data)
    assert result == expected_output

def test_your_function_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

### Test Types

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test interactions between components
3. **Configuration Tests**: Validate YAML/TOML files
4. **Import Tests**: Verify modules can be imported

---

## Code Style

### Python Code

We use **Ruff** for linting and formatting.

**Rules**:
- Line length: 120 characters max
- Type hints required for new functions
- Docstrings required (Google style)
- Follow PEP 8

**Run formatting**:

```bash
# Check formatting
ruff format --check .

# Auto-format
ruff format .

# Check linting
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### Type Hints

All new functions must have type hints:

```python
def create_material(
    name: str = "New Material",
    color: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5
) -> bpy.types.Material:
    """
    Create a material with specified properties.

    Args:
        name: Name of the material
        color: RGBA color tuple (values 0.0-1.0)
        metallic: Metallic value (0.0-1.0)
        roughness: Roughness value (0.0-1.0)

    Returns:
        Created Blender material

    Raises:
        ValueError: If color values are out of range
    """
    # Implementation
```

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short one-line description.

    Longer description if needed, explaining the function's
    behavior in more detail.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When this happens
        TypeError: When that happens

    Examples:
        >>> function_name("test", 5)
        True
    """
```

### Bash Scripts

- Use `#!/bin/bash` shebang
- Set `set -e` for error handling
- Comment complex sections
- Validate all inputs
- Use meaningful variable names

---

## Commit Guidelines

### Commit Messages

Follow conventional commit format:

```
type(scope): short description

Longer description if needed.

Fixes #123
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples**:

```
feat(demos): add materials showcase script

Add new demo showing 16 different material types including
metals, glass, plastics, and subsurface materials.

Closes #45
```

```
fix(build): remove python3.12-distutils dependency

Python 3.12 removed distutils from stdlib (PEP 632).
This package doesn't exist and causes build failures.

Fixes #67
```

### Commit Size

- **Small commits** are better than large ones
- Each commit should represent a single logical change
- Should be able to revert individual commits safely

---

## Pull Request Process

### Before Submitting

1. ✅ Code follows style guidelines (run `ruff check .`)
2. ✅ All tests pass (run `pytest`)
3. ✅ Test coverage is adequate (run `pytest --cov`)
4. ✅ Type hints added (run `mypy`)
5. ✅ Documentation updated if needed
6. ✅ Commit messages follow guidelines
7. ✅ Branch is up to date with main

### Submitting

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill out PR template** with:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if UI changes)

4. **Wait for review**:
   - Address reviewer feedback
   - Make requested changes
   - Re-request review when ready

### PR Requirements

- [ ] All CI checks must pass
- [ ] At least one approval from maintainer
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] Documentation updated
- [ ] Tests added/updated

### After Merge

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Delete your feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Search closed issues
3. Try to reproduce with latest version
4. Gather relevant information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12.0]
- Blender-wheel version: [e.g., 1.0.0]

**Additional context**
- Error messages
- Logs
- Screenshots
```

---

## Suggesting Enhancements

### Enhancement Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
How you'd like the feature to work.

**Describe alternatives considered**
Other approaches you've thought about.

**Additional context**
- Use cases
- Examples
- Mockups
```

---

## Development Tips

### Testing Without Blender

Most tests can run without Blender installed by using mocks:

```python
import pytest

def test_with_mock_bpy(mocker):
    mock_bpy = mocker.patch('bpy')
    # Test your code
```

### Local Build Testing

Test the build script in Docker to avoid polluting your system:

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  bash -c "apt-get update && apt-get install -y sudo && ./build_blender_wheel.sh --yes"
```

### Debugging CI Failures

```bash
# Run the same checks locally
ruff check .
ruff format --check .
pytest --cov=blender-demo
mypy blender-demo/scripts/
```

---

## Getting Help

- **Issues**: Open an issue for questions
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Check docs first

---

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in CHANGELOG
- Added to contributors list

---

Thank you for contributing! 🎉
