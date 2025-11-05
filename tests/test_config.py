"""Tests for configuration and build files."""
import yaml
import json
from pathlib import Path


# CloudFormation-specific YAML tag handlers
def cloudformation_constructor(loader, tag_suffix, node):
    """Generic constructor for CloudFormation intrinsic functions."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Register CloudFormation tags
yaml.SafeLoader.add_multi_constructor('!', cloudformation_constructor)


def test_cloudformation_template_valid():
    """Test that CloudFormation template is valid YAML."""
    cf_path = Path(__file__).parent.parent / "cf" / "codebuild.yml"
    assert cf_path.exists(), "CloudFormation template not found"

    with open(cf_path) as f:
        data = yaml.safe_load(f)

    # Validate basic structure
    assert "AWSTemplateFormatVersion" in data
    assert "Description" in data
    assert "Parameters" in data
    assert "Resources" in data

    # Validate parameters exist
    assert "GitHubSourceRepo" in data["Parameters"]
    assert "BlenderRepoURL" in data["Parameters"]
    assert "OutputBucketName" in data["Parameters"]

    # Validate resources exist
    assert "CodeBuildAccessPolicy" in data["Resources"]
    assert "CodeBuildServiceRole" in data["Resources"]
    assert "BlenderWhlBuildProject" in data["Resources"]


def test_buildspec_valid():
    """Test that buildspec is valid YAML."""
    buildspec_path = Path(__file__).parent.parent / "buildspec.yml" / "blender-whl.yml"
    assert buildspec_path.exists(), "Buildspec not found"

    with open(buildspec_path) as f:
        data = yaml.safe_load(f)

    # Validate basic structure
    assert "version" in data
    assert "phases" in data

    # Validate phases
    assert "install" in data["phases"]
    assert "pre_build" in data["phases"]
    assert "build" in data["phases"]
    assert "post_build" in data["phases"]


def test_pyproject_toml_valid():
    """Test that pyproject.toml is valid."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml not found"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    # Validate basic structure
    assert "project" in data
    assert "build-system" in data

    # Validate project metadata
    assert "name" in data["project"]
    assert "version" in data["project"]
    assert "description" in data["project"]
    assert "requires-python" in data["project"]
    assert "dependencies" in data["project"]


def test_requirements_txt_exists():
    """Test that requirements.txt exists and has content."""
    req_path = Path(__file__).parent.parent / "blender-demo" / "requirements.txt"
    assert req_path.exists(), "requirements.txt not found"

    with open(req_path) as f:
        content = f.read()

    assert "numpy" in content
    assert "pillow" in content
    # Verify versions are pinned (no >= operators)
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    for line in lines:
        if '=' in line:
            assert '==' in line, f"Dependency not pinned: {line}"
