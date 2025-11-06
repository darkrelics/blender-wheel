# Blender Python Module Demo

This simple demo project demonstrates how to use the Blender Python module (bpy) to programmatically create and render 3D content.

## Project Structure

```
blender-demo/
├── README.md
├── requirements.txt
├── demo.py
├── materials_demo.py
├── animation_demo.py
├── generate_scene_assets.py
└── scripts/
    ├── render_batch.py
    └── utils.py
```

## Installation

1. Install the Blender Python module:

```bash
pip install -r requirements.txt
```

## Usage

Run any of the demo scripts:

```bash
python demo.py
python materials_demo.py
python animation_demo.py
python generate_scene_assets.py
```

## Demo Script Details

Each script demonstrates different aspects of the Blender Python API:

- `demo.py`: Basic scene creation and rendering
- `materials_demo.py`: Working with materials and textures
- `animation_demo.py`: Creating simple animations
- `generate_scene_assets.py`: Complete scene with props, characters, and environment (NEW!)
- `scripts/render_batch.py`: Batch rendering multiple scenes
- `scripts/utils.py`: Helper functions for common tasks

### Scene Asset Generator

The `generate_scene_assets.py` script creates a complete game-ready scene with:

**Assets Created:**
- Wooden crates (props)
- Metal barrels (props)
- Lamp posts with working lights
- Character placeholder (capsule mesh)
- Textured ground plane
- Atmospheric lighting (sun + sky)

**Outputs:**
- `scene_assets.blend` - Full Blender scene file
- `scene_wide.png` - Wide establishing shot
- `scene_character.png` - Character close-up
- `scene_topdown.png` - Top-down tactical view
- `scene_props.png` - Detailed prop view

Run it with:
```bash
python generate_scene_assets.py
```

Output will be in `output/scene_assets/` directory.