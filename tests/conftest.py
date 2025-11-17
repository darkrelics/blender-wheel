"""Pytest configuration and fixtures for blender-wheel tests."""
import sys
from pathlib import Path

import pytest

# Add blender-demo to Python path so we can import from scripts module
# (Demo scripts are standalone, not an importable package)
demo_path = Path(__file__).parent.parent / "blender-demo"
if str(demo_path) not in sys.path:
    sys.path.insert(0, str(demo_path))


@pytest.fixture
def sample_color():
    """Provide a sample RGBA color tuple."""
    return (0.8, 0.2, 0.2, 1.0)


@pytest.fixture
def sample_location():
    """Provide a sample 3D location tuple."""
    return (0, 0, 1)


@pytest.fixture
def sample_rotation():
    """Provide a sample rotation tuple."""
    return (0, 0, 0)
