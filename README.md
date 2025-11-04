# Blender Wheel

This repository contains templates and configuration for building Blender 4.4 as a Python wheel package using AWS CodeBuild. This enables integration of Blender's 3D capabilities into Python projects.

## Overview

The Blender wheel package provides the Blender Python API (bpy) as an importable Python module, allowing programmatic creation, manipulation, and rendering of 3D content using Blender's engine within Python applications.

## Features

- Build process for Blender 4.4 Python module using AWS CodeBuild
- CloudFormation template for infrastructure setup
- Build configuration for Blender 4.4
- Produces a pip-installable wheel file
- Support for Python 3.12

## Prerequisites

- AWS Account with permissions to create CloudFormation stacks, IAM roles, and CodeBuild projects
- S3 bucket for storing the built wheel file
- Basic knowledge of AWS services

## Deployment

### Using the AWS Console

1. Navigate to the CloudFormation console in your AWS account
2. Create a new stack and upload the `cf/codebuild.yml` file
3. Provide the required parameters:
   - GitHub repository URL
   - Blender repository URL (default is set to the official Blender repo)
   - Output S3 bucket name
4. Create the stack and wait for completion
5. The CodeBuild project will be created and ready to run

### Using AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name blender-wheel-build \
  --template-body file://cf/codebuild.yml \
  --parameters \
    ParameterKey=OutputBucketName,ParameterValue=your-output-bucket \
    ParameterKey=GitHubSourceRepo,ParameterValue=https://github.com/yourusername/blender-wheel.git \
  --capabilities CAPABILITY_IAM
```

## Running the Build

After deploying the CloudFormation stack:

1. Go to the CodeBuild console
2. Find the "Blender-4.4-Whl-Build" project
3. Start the build
4. Once complete, the wheel file will be available in your S3 bucket

## Installation of the Built Wheel

Once the build is complete and the wheel file is in your S3 bucket, you can install it using pip:

```bash
# Download from S3
aws s3 cp s3://your-output-bucket/blender_bpy_module-4.4.whl .

# Install with pip
pip install blender_bpy_module-4.4.whl
```

## Usage Example

After installation, you can import and use the Blender API in your Python code:

```python
import bpy

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Add a material
material = bpy.data.materials.new(name="Material")
material.use_nodes = True
bpy.context.active_object.data.materials.append(material)

# Render to file
bpy.context.scene.render.filepath = "/tmp/render.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)

print("Render complete")
```

## Project Structure

- `cf/codebuild.yml` - CloudFormation template for setting up the CodeBuild project
- `buildspec.yml/blender-whl.yml` - Build specification for CodeBuild to compile Blender
- `blender-demo/` - Demo applications showcasing Blender Python API usage
- `tests/` - Test suite for validating project functionality
- `pyproject.toml` - Project metadata and build configuration
- `README.md` - This documentation file

## Development

### Running Tests

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=blender-demo --cov-report=html
```

### Code Quality

Format code with ruff:

```bash
ruff check .
ruff format .
```

## Customization

The build can be modified by editing the following files:

- `buildspec.yml/blender-whl.yml`: Modify build parameters, Python version, or dependencies
- `cf/codebuild.yml`: Adjust compute resources, environment variables, or timeout settings

## Troubleshooting

Common issues:

- **Build timeout**: Increase the `TimeoutInMinutes` value in the CodeBuild project configuration
- **Insufficient resources**: Change the `ComputeType` to a larger instance size
- **Compilation errors**: Check the CodeBuild logs for specific error messages

## License

This project is provided under the [Apache License 2.0](LICENSE).

## Credits

- Blender is developed by the Blender Foundation and licensed under GPL
- This project provides infrastructure for building Blender as a Python module