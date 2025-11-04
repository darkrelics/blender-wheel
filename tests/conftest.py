"""Pytest configuration and fixtures for blender-wheel tests."""
import pytest
import sys
from pathlib import Path

# Add blender-demo to Python path for imports
demo_path = Path(__file__).parent.parent / "blender-demo"
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
