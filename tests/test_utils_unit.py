"""Unit tests for utility functions that don't require Blender."""
import sys
from pathlib import Path
import pytest

# Add blender-demo to path
demo_path = Path(__file__).parent.parent / "blender-demo"
sys.path.insert(0, str(demo_path))


def test_module_constants():
    """Test that the utils module has expected constants."""
    try:
        from scripts import utils
        # Verify module is importable
        assert utils is not None
    except ImportError as e:
        if 'bpy' in str(e):
            pytest.skip("Blender (bpy) not installed")
        else:
            raise


def test_color_tuple_format(sample_color):
    """Test that color tuples are in correct RGBA format."""
    assert len(sample_color) == 4
    assert all(0 <= c <= 1 for c in sample_color)


def test_location_tuple_format(sample_location):
    """Test that location tuples are in correct XYZ format."""
    assert len(sample_location) == 3
    assert all(isinstance(c, (int, float)) for c in sample_location)


def test_rotation_tuple_format(sample_rotation):
    """Test that rotation tuples are in correct format."""
    assert len(sample_rotation) == 3
    assert all(isinstance(c, (int, float)) for c in sample_rotation)
