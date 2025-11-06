# Getting Started with Blender-Wheel

This guide walks you through building Blender as a Python module, generating 3D assets, and using them in your projects.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building the Blender Wheel](#building-the-blender-wheel)
3. [Installing the Wheel](#installing-the-wheel)
4. [Generating Your First Assets](#generating-your-first-assets)
5. [Using Assets in Your Project](#using-assets-in-your-project)
6. [Next Steps](#next-steps)

---

## Prerequisites

### AWS Account Setup

You'll need an AWS account with:
- Permission to create CloudFormation stacks
- Permission to create IAM roles
- Permission to create CodeBuild projects
- An S3 bucket for storing the built wheel

### Local Development Setup

```bash
# Required software
- Python 3.12+
- AWS CLI (configured with credentials)
- Git
```

Install AWS CLI and configure:
```bash
pip install awscli
aws configure
```

---

## Building the Blender Wheel

### Step 1: Clone the Repository

```bash
git clone https://github.com/darkrelics/blender-wheel.git
cd blender-wheel
```

### Step 2: Deploy the Build Infrastructure

Using AWS CLI:

```bash
# Create S3 bucket for artifacts (if you don't have one)
aws s3 mb s3://your-blender-wheel-bucket --region us-east-1

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name blender-wheel-build \
  --template-body file://cf/codebuild.yml \
  --parameters \
    ParameterKey=OutputBucketName,ParameterValue=your-blender-wheel-bucket \
    ParameterKey=GitHubSourceRepo,ParameterValue=https://github.com/darkrelics/blender-wheel.git \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Wait for stack creation (5-10 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name blender-wheel-build \
  --region us-east-1

echo "Stack created successfully!"
```

### Step 3: Start the Build

```bash
# Get the CodeBuild project name
PROJECT_NAME=$(aws cloudformation describe-stacks \
  --stack-name blender-wheel-build \
  --query 'Stacks[0].Outputs[?OutputKey==`CodeBuildProjectName`].OutputValue' \
  --output text \
  --region us-east-1)

# Start the build
aws codebuild start-build \
  --project-name Blender-Whl-Build \
  --region us-east-1

echo "Build started! This will take 45-60 minutes."
```

### Step 4: Monitor the Build

```bash
# Check build status (run periodically)
aws codebuild list-builds-for-project \
  --project-name Blender-Whl-Build \
  --region us-east-1

# Or watch in AWS Console
# Navigate to: CodeBuild -> Build projects -> Blender-Whl-Build
```

### Step 5: Download the Wheel

Once the build completes:

```bash
# Download from S3
aws s3 cp s3://your-blender-wheel-bucket/blender_bpy_module.whl ./

# Verify the file
ls -lh blender_bpy_module.whl
```

**Expected file size**: ~500MB - 1.5GB

---

## Installing the Wheel

### Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3.12 -m venv blender-env

# Activate it
source blender-env/bin/activate  # Linux/Mac
# OR
blender-env\Scripts\activate     # Windows
```

### Install the Wheel

```bash
# Install the wheel
pip install blender_bpy_module.whl

# Install demo dependencies
cd blender-wheel
pip install -r blender-demo/requirements.txt

# Verify installation
python -c "import bpy; print(f'Blender version: {bpy.app.version_string}')"
```

**Expected output**: `Blender version: 4.4.0`

---

## Generating Your First Assets

### Option 1: Run the Quick Demo

```bash
cd blender-demo
python demo.py
```

**Output**: `output/demo_render.png` - Simple scene with cube, sphere, cone

### Option 2: Generate a Complete Scene

```bash
python generate_scene_assets.py
```

**This creates**:
- 📁 `output/scene_assets/` directory with:
  - `scene_assets.blend` - Full Blender scene file
  - `scene_wide.png` - Wide shot (1920x1080)
  - `scene_character.png` - Character close-up
  - `scene_topdown.png` - Top-down view
  - `scene_props.png` - Props detail

**Assets included**:
- Wooden crates (game props)
- Metal barrels (game props)
- Lamp posts with lights
- Character placeholder
- Textured ground
- Atmospheric lighting

**Time**: ~5-15 minutes depending on your CPU

### Option 3: Try Other Demos

```bash
# Materials showcase
python materials_demo.py
# Output: output/materials_demo.png (16 different materials)

# Animation example
python animation_demo.py
# Output: output/animation/frame_001.png

# Batch rendering from config
python scripts/render_batch.py --create-sample-config --config config/sample.json
python scripts/render_batch.py --config config/sample.json
# Output: output/batch/<timestamp>/*.png
```

---

## Using Assets in Your Project

### Method 1: Use the .blend File

The generated `.blend` file can be opened in Blender or loaded programmatically:

```python
import bpy

# Load the scene
bpy.ops.wm.open_mainfile(filepath="output/scene_assets/scene_assets.blend")

# Access objects
crate = bpy.data.objects.get("Crate")
if crate:
    # Modify the crate
    crate.location = (5, 5, 0)

# Export to other formats
bpy.ops.export_scene.gltf(
    filepath="output/scene_assets.gltf",
    export_format='GLTF_SEPARATE'
)
```

### Method 2: Export Assets to Game Engine Formats

Create an export script:

```python
# export_for_unity.py
import bpy
import os

output_dir = "output/unity_assets"
os.makedirs(output_dir, exist_ok=True)

# Load scene
bpy.ops.wm.open_mainfile(filepath="output/scene_assets/scene_assets.blend")

# Export each object as FBX
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Export
        filepath = os.path.join(output_dir, f"{obj.name}.fbx")
        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            axis_forward='-Z',
            axis_up='Y'
        )
        print(f"Exported: {filepath}")

print("All assets exported for Unity!")
```

Run it:
```bash
python export_for_unity.py
```

### Method 3: Integrate with Python Game/Application

```python
# your_game.py
import pygame
import bpy

# Use Blender for asset pipeline
def generate_level_assets():
    """Generate assets programmatically for your game."""
    import bpy

    # Create assets
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    # Add material
    mat = bpy.data.materials.new(name="GameMaterial")
    cube.data.materials.append(mat)

    # Render icon
    bpy.context.scene.render.filepath = "assets/cube_icon.png"
    bpy.ops.render.render(write_still=True)

# In your game initialization
generate_level_assets()

# Then use pygame to load the rendered images
icon = pygame.image.load("assets/cube_icon.png")
```

### Method 4: Create Asset Generation Pipeline

```python
# asset_pipeline.py
"""
Production asset pipeline using Blender-Wheel.
Generates all game assets automatically.
"""
import sys
sys.path.append("blender-demo")
from scripts.utils import *

def generate_all_game_assets(config):
    """Generate complete asset library from config."""

    for asset_def in config['assets']:
        reset_to_factory()

        # Create asset
        obj = create_object(
            obj_type=asset_def['type'],
            location=asset_def['location'],
            size=asset_def['size']
        )

        # Add material
        mat = create_material(
            name=asset_def['material']['name'],
            color=asset_def['material']['color']
        )
        obj.data.materials.append(mat)

        # Setup camera
        setup_camera(location=(5, -5, 5))
        setup_lighting("studio")

        # Render multiple angles
        angles = ['front', 'side', 'top', 'perspective']
        for angle in angles:
            # Position camera for angle
            render_to_file(f"assets/{asset_def['name']}_{angle}.png")

# Run pipeline
with open('asset_config.json') as f:
    config = json.load(f)

generate_all_game_assets(config)
```

---

## Next Steps

### Learn More About Blender Python API

```python
# Explore available objects
import bpy
print(dir(bpy.ops))  # All operations
print(dir(bpy.data))  # All data blocks

# Official docs
# https://docs.blender.org/api/current/
```

### Explore the Utils Library

The `scripts/utils.py` provides helper functions:

```python
from scripts.utils import *

# Scene setup
reset_to_factory()
setup_render_settings(samples=128)
setup_camera(location=(10, -10, 5))
setup_lighting("three_point")

# Create objects
cube = create_object("CUBE", size=2, location=(0, 0, 1))
sphere = create_object("SPHERE", size=1, location=(3, 0, 1))

# Materials
red_mat = create_material("Red", color=(0.8, 0.1, 0.1, 1.0))
cube.data.materials.append(red_mat)

# Render
render_to_file("output/my_scene.png")
```

### Customize the Build

Edit build parameters:
- **Build spec**: `buildspec.yml/blender-whl.yml`
- **CloudFormation**: `cf/codebuild.yml`

Add features like:
- Custom Blender patches
- Additional Python modules
- Different Python versions
- Platform-specific builds

### Run Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=blender-demo --cov-report=html
```

### Contribute

See `CONTRIBUTING.md` for guidelines on:
- Reporting issues
- Submitting pull requests
- Code style
- Testing requirements

---

## Troubleshooting

### Build Fails

**Issue**: Build times out after 60 minutes

**Solution**: Increase timeout in `cf/codebuild.yml`:
```yaml
TimeoutInMinutes: 120  # Increase from 60
```

**Issue**: Out of memory errors

**Solution**: Increase compute size:
```yaml
ComputeType: BUILD_GENERAL1_2XLARGE  # Upgrade from LARGE
```

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'bpy'`

**Solution**:
- Ensure wheel is installed: `pip list | grep blender`
- Check Python version matches: `python --version` (must be 3.12)
- Reinstall: `pip uninstall blender_bpy_module && pip install blender_bpy_module.whl`

### Rendering Issues

**Issue**: Renders take too long

**Solution**: Reduce samples in render settings:
```python
setup_render_settings(samples=64)  # Lower from 128+
bpy.context.scene.render.resolution_percentage = 50  # Lower resolution
```

**Issue**: Black renders or missing objects

**Solution**: Check camera and lighting:
```python
# Ensure camera is set
print(bpy.context.scene.camera)

# List all lights
lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
print(f"Found {len(lights)} lights")
```

---

## Support

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/darkrelics/blender-wheel/issues
- **Blender Docs**: https://docs.blender.org/api/current/

---

## Quick Reference

```bash
# Build
aws cloudformation create-stack --stack-name blender-wheel-build --template-body file://cf/codebuild.yml --capabilities CAPABILITY_IAM
aws codebuild start-build --project-name Blender-Whl-Build

# Install
pip install blender_bpy_module.whl
pip install -r blender-demo/requirements.txt

# Generate
cd blender-demo
python generate_scene_assets.py

# Test
pytest

# Export for game engine
python export_for_unity.py  # Your custom script
```

**Estimated Total Time**: 1-2 hours (including build time)

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
