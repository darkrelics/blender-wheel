"""Test that all demo modules can be imported successfully."""
import sys
from pathlib import Path

import pytest

# Add blender-demo to path
demo_path = Path(__file__).parent.parent / "blender-demo"
sys.path.insert(0, str(demo_path))


def test_import_demo_script():
    """Test that demo.py can be imported."""
    # Note: This test will fail without Blender installed
    # It's here to validate the code structure is importable
    try:
        import demo
        assert hasattr(demo, 'main')
        assert hasattr(demo, 'reset_scene')
        assert hasattr(demo, 'create_camera')
        assert hasattr(demo, 'create_light')
        assert hasattr(demo, 'create_floor')
        assert hasattr(demo, 'create_objects')
        assert hasattr(demo, 'render_scene')
    except ImportError as e:
        if 'bpy' in str(e):
            pytest.skip("Blender (bpy) not installed - skipping import test")
        else:
            raise


def test_import_animation_demo():
    """Test that animation_demo.py can be imported."""
    try:
        import animation_demo
        assert hasattr(animation_demo, 'main')
        assert hasattr(animation_demo, 'reset_scene')
        assert hasattr(animation_demo, 'setup_environment')
        assert hasattr(animation_demo, 'create_material')
    except ImportError as e:
        if 'bpy' in str(e):
            pytest.skip("Blender (bpy) not installed - skipping import test")
        else:
            raise


def test_import_materials_demo():
    """Test that materials_demo.py can be imported."""
    try:
        import materials_demo
        assert hasattr(materials_demo, 'main')
        assert hasattr(materials_demo, 'reset_scene')
        assert hasattr(materials_demo, 'setup_environment')
        assert hasattr(materials_demo, 'create_metal_material')
        assert hasattr(materials_demo, 'create_glass_material')
    except ImportError as e:
        if 'bpy' in str(e) or 'numpy' in str(e):
            pytest.skip(f"Required dependency not installed - skipping import test: {e}")
        else:
            raise


def test_import_render_batch():
    """Test that render_batch.py can be imported."""
    try:
        from scripts import render_batch
        assert hasattr(render_batch, 'main')
        assert hasattr(render_batch, 'create_scene')
        assert hasattr(render_batch, 'render_scenes_from_config')
        assert hasattr(render_batch, 'create_sample_config')
    except ImportError as e:
        if 'bpy' in str(e):
            pytest.skip("Blender (bpy) not installed - skipping import test")
        else:
            raise


def test_import_utils():
    """Test that utils.py can be imported."""
    try:
        from scripts import utils
        assert hasattr(utils, 'reset_to_factory')
        assert hasattr(utils, 'setup_render_settings')
        assert hasattr(utils, 'setup_camera')
        assert hasattr(utils, 'setup_lighting')
        assert hasattr(utils, 'create_material')
        assert hasattr(utils, 'create_object')
        assert hasattr(utils, 'render_to_file')
    except ImportError as e:
        if 'bpy' in str(e):
            pytest.skip("Blender (bpy) not installed - skipping import test")
        else:
            raise
