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
```

## Demo Script Details

Each script demonstrates different aspects of the Blender Python API:

- `demo.py`: Basic scene creation and rendering
- `materials_demo.py`: Working with materials and textures
- `animation_demo.py`: Creating simple animations
- `scripts/render_batch.py`: Batch rendering multiple scenes
- `scripts/utils.py`: Helper functions for common tasks