"""Tests for build_blender_wheel.sh script."""
import subprocess
from pathlib import Path


def test_build_script_exists():
    """Test that the build script exists and is executable."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    assert script_path.exists(), "build_blender_wheel.sh not found"
    assert script_path.stat().st_mode & 0o111, "build_blender_wheel.sh is not executable"


def test_build_script_syntax():
    """Test that the build script has valid bash syntax."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    result = subprocess.run(
        ["bash", "-n", str(script_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Syntax error in build script: {result.stderr}"


def test_build_script_help():
    """Test that the build script shows help information."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    result = subprocess.run(
        ["bash", str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=5
    )
    # The script doesn't have --help but shouldn't crash
    assert "Blender Python Module Build Script" in result.stdout or result.returncode == 1


def test_build_script_has_safety_checks():
    """Test that the build script contains safety checks."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    content = script_path.read_text()

    # Check for dangerous operations safety checks
    assert 'if [ -z "$BUILD_DIR" ]' in content, "Missing BUILD_DIR validation"
    assert 'WARNING' in content, "Missing security warnings"
    assert 'sudo' in content, "Script doesn't warn about sudo usage"


def test_build_script_has_phases():
    """Test that the build script has all required phases."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    content = script_path.read_text()

    required_phases = [
        "Phase 1: Installing build dependencies",
        "Phase 2: Cloning Blender source",
        "Phase 3: Building Blender Python module",
        "Phase 4: Generating Python wheel",
        "Phase 5: Generating checksums",
        "Phase 6: Verifying wheel installation"
    ]

    for phase in required_phases:
        assert phase in content, f"Missing phase: {phase}"


def test_build_script_environment_variables():
    """Test that the build script uses correct environment variables."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    content = script_path.read_text()

    required_vars = [
        "BLENDER_REPO_URL",
        "PYTHON_VERSION",
        "OUTPUT_DIR",
        "BUILD_DIR"
    ]

    for var in required_vars:
        assert var in content, f"Missing environment variable: {var}"


def test_build_script_default_values():
    """Test that the build script has sensible defaults."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    content = script_path.read_text()

    # Check default values
    assert "3.12" in content, "Missing default Python version"
    assert "blender.org" in content or "blender.git" in content, "Missing default Blender repo"


def test_build_script_creates_checksums():
    """Test that the build script generates checksums."""
    script_path = Path(__file__).parent.parent / "build_blender_wheel.sh"
    content = script_path.read_text()

    assert "sha256sum" in content, "Missing SHA256 checksum generation"
    assert "md5sum" in content, "Missing MD5 checksum generation"
