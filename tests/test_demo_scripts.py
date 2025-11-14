"""Tests for demo scripts structure and documentation."""
import ast
import sys
from pathlib import Path

# Add blender-demo to path
demo_path = Path(__file__).parent.parent / "blender-demo"
sys.path.insert(0, str(demo_path))


def test_all_demo_scripts_exist():
    """Test that all required demo scripts exist."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    required_scripts = [
        "demo.py",
        "animation_demo.py",
        "materials_demo.py",
        "generate_scene_assets.py"
    ]

    for script in required_scripts:
        script_path = demo_dir / script
        assert script_path.exists(), f"Demo script {script} not found"


def test_demo_scripts_have_docstrings():
    """Test that demo scripts have module docstrings."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = [
        "demo.py",
        "animation_demo.py",
        "materials_demo.py",
        "generate_scene_assets.py"
    ]

    for script in demo_scripts:
        script_path = demo_dir / script
        with open(script_path) as f:
            tree = ast.parse(f.read())

        module_docstring = ast.get_docstring(tree)
        assert module_docstring is not None, f"{script} missing module docstring"
        assert len(module_docstring) > 10, f"{script} docstring too short"


def test_demo_scripts_have_main():
    """Test that demo scripts have main() function."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = [
        "demo.py",
        "animation_demo.py",
        "materials_demo.py",
        "generate_scene_assets.py"
    ]

    for script in demo_scripts:
        script_path = demo_dir / script
        content = script_path.read_text()
        assert "def main(" in content, f"{script} missing main() function"
        assert 'if __name__ == "__main__"' in content, f"{script} missing main guard"


def test_demo_scripts_import_bpy():
    """Test that demo scripts import bpy."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = [
        "demo.py",
        "animation_demo.py",
        "materials_demo.py",
        "generate_scene_assets.py"
    ]

    for script in demo_scripts:
        script_path = demo_dir / script
        content = script_path.read_text()
        assert "import bpy" in content, f"{script} doesn't import bpy"


def test_demo_scripts_syntax_valid():
    """Test that demo scripts have valid Python syntax."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = list(demo_dir.glob("*.py"))

    for script_path in demo_scripts:
        with open(script_path) as f:
            try:
                ast.parse(f.read())
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {script_path.name}: {e}")


def test_utils_module_exists():
    """Test that utils module exists."""
    utils_path = Path(__file__).parent.parent / "blender-demo" / "scripts" / "utils.py"
    assert utils_path.exists(), "scripts/utils.py not found"


def test_utils_has_helper_functions():
    """Test that utils.py has expected helper functions."""
    utils_path = Path(__file__).parent.parent / "blender-demo" / "scripts" / "utils.py"
    content = utils_path.read_text()

    expected_functions = [
        "def create_material",
        "def create_object",
        "def setup_render_settings",
        "def setup_camera",
        "def setup_lighting",
        "def save_file",
        "def render_to_file"
    ]

    for func in expected_functions:
        assert func in content, f"utils.py missing function: {func}"


def test_utils_functions_have_type_hints():
    """Test that utils.py functions have type hints."""
    utils_path = Path(__file__).parent.parent / "blender-demo" / "scripts" / "utils.py"
    content = utils_path.read_text()

    # Check for type hint syntax
    type_hint_indicators = [
        "->",  # Return type hints
        ": str",  # Parameter type hints
        ": int",
        ": float",
        ": bool",
        "tuple[float"
    ]

    found_hints = sum(1 for indicator in type_hint_indicators if indicator in content)
    assert found_hints >= 5, "utils.py missing type hints"


def test_utils_functions_have_docstrings():
    """Test that utils.py functions have docstrings."""
    utils_path = Path(__file__).parent.parent / "blender-demo" / "scripts" / "utils.py"

    with open(utils_path) as f:
        tree = ast.parse(f.read())

    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert len(functions) > 0, "No functions found in utils.py"

    functions_with_docstrings = [f for f in functions if ast.get_docstring(f)]
    coverage = len(functions_with_docstrings) / len(functions)

    assert coverage >= 0.8, f"Only {coverage*100:.0f}% of functions have docstrings (need 80%)"


def test_requirements_txt_exists():
    """Test that requirements.txt exists."""
    req_path = Path(__file__).parent.parent / "blender-demo" / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found"


def test_requirements_txt_has_dependencies():
    """Test that requirements.txt lists dependencies."""
    req_path = Path(__file__).parent.parent / "blender-demo" / "requirements.txt"
    content = req_path.read_text()

    required_deps = ["numpy", "pillow"]
    for dep in required_deps:
        assert dep.lower() in content.lower(), f"requirements.txt missing {dep}"


def test_scripts_directory_exists():
    """Test that scripts directory exists."""
    scripts_path = Path(__file__).parent.parent / "blender-demo" / "scripts"
    assert scripts_path.exists(), "scripts directory not found"
    assert scripts_path.is_dir(), "scripts is not a directory"


def test_output_directory_structure():
    """Test that output directory structure is documented."""
    # Check if any script mentions output directory
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = list(demo_dir.glob("*.py"))

    mentions_output = False
    for script_path in demo_scripts:
        content = script_path.read_text()
        if "output" in content.lower():
            mentions_output = True
            break

    assert mentions_output, "No script documents output directory structure"


def test_demo_scripts_have_shebang():
    """Test that demo scripts have proper shebang."""
    demo_dir = Path(__file__).parent.parent / "blender-demo"
    demo_scripts = [
        "demo.py",
        "animation_demo.py",
        "materials_demo.py",
        "generate_scene_assets.py"
    ]

    for script in demo_scripts:
        script_path = demo_dir / script
        with open(script_path) as f:
            first_line = f.readline()

        assert first_line.startswith("#!"), f"{script} missing shebang"
        assert "python" in first_line.lower(), f"{script} shebang doesn't reference python"
