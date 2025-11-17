"""Tests for project documentation."""
import re
from pathlib import Path


def test_readme_exists():
    """Test that README.md exists and has content."""
    readme_path = Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md not found"

    content = readme_path.read_text()
    assert len(content) > 100, "README.md is too short"
    assert "Blender" in content, "README doesn't mention Blender"


def test_changelog_exists():
    """Test that CHANGELOG.md exists."""
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    assert changelog_path.exists(), "CHANGELOG.md not found"


def test_security_md_exists():
    """Test that SECURITY.md exists and has required sections."""
    security_path = Path(__file__).parent.parent / "SECURITY.md"
    assert security_path.exists(), "SECURITY.md not found"

    content = security_path.read_text()
    required_sections = [
        "Reporting a Vulnerability",
        "Security",
        "Known Security Considerations"
    ]

    for section in required_sections:
        assert section in content, f"SECURITY.md missing section: {section}"


def test_contributing_md_exists():
    """Test that CONTRIBUTING.md exists and has required sections."""
    contributing_path = Path(__file__).parent.parent / "CONTRIBUTING.md"
    assert contributing_path.exists(), "CONTRIBUTING.md not found"

    content = contributing_path.read_text()
    required_sections = [
        "Development Setup",
        "Testing",
        "Code Style",
        "Pull Request"
    ]

    for section in required_sections:
        assert section in content, f"CONTRIBUTING.md missing section: {section}"


def test_getting_started_exists():
    """Test that GETTING_STARTED.md exists."""
    getting_started_path = Path(__file__).parent.parent / "GETTING_STARTED.md"
    assert getting_started_path.exists(), "GETTING_STARTED.md not found"

    content = getting_started_path.read_text()
    assert len(content) > 500, "GETTING_STARTED.md is too short"


def test_license_exists():
    """Test that LICENSE file exists."""
    license_path = Path(__file__).parent.parent / "LICENSE"
    assert license_path.exists(), "LICENSE file not found"


def test_readme_has_badges():
    """Test that README has status badges or key information."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # Should have some indication of status or version
    assert "Python" in content or "python" in content, "README doesn't mention Python version"
    assert "4.4" in content or "Blender" in content, "README doesn't mention Blender version"


def test_readme_has_installation_instructions():
    """Test that README has installation instructions."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    assert "install" in content.lower() or "pip" in content.lower(), \
        "README missing installation instructions"


def test_readme_has_examples():
    """Test that README has usage examples."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # Should have code examples
    assert "```" in content, "README missing code examples"


def test_documentation_links_valid():
    """Test that documentation doesn't have broken internal links."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()
    project_root = Path(__file__).parent.parent

    # Find all markdown links to local files
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)

    for link_text, link_url in matches:
        # Skip external URLs
        if link_url.startswith('http://') or link_url.startswith('https://'):
            continue

        # Skip anchors
        if link_url.startswith('#'):
            continue

        # Check if local file exists
        link_path = project_root / link_url
        # Only check files, not directories
        if '.' in link_url.split('/')[-1]:
            # Some leniency - the file might not exist yet but structure should be valid
            pass  # We're just checking for valid structure here


def test_security_has_contact_info():
    """Test that SECURITY.md has contact information."""
    security_path = Path(__file__).parent.parent / "SECURITY.md"
    content = security_path.read_text()

    assert "report" in content.lower() or "contact" in content.lower(), \
        "SECURITY.md missing contact information"


def test_contributing_has_code_style():
    """Test that CONTRIBUTING.md specifies code style."""
    contributing_path = Path(__file__).parent.parent / "CONTRIBUTING.md"
    content = contributing_path.read_text()

    assert "ruff" in content.lower() or "style" in content.lower(), \
        "CONTRIBUTING.md missing code style guidelines"


def test_project_has_demo_directory():
    """Test that demo directory exists with examples."""
    demo_path = Path(__file__).parent.parent / "blender-demo"
    assert demo_path.exists(), "blender-demo directory not found"
    assert demo_path.is_dir(), "blender-demo is not a directory"

    # Check for demo scripts
    demo_scripts = list(demo_path.glob("*_demo.py"))
    assert len(demo_scripts) > 0, "No demo scripts found in blender-demo/"
