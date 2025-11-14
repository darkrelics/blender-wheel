#!/usr/bin/env python3
"""
Basic Blender Demo Script
-------------------------
Creates a simple 3D scene with geometric primitives and renders it.
"""
import os
import sys

import bpy

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.constants import (
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    DEFAULT_RESOLUTION_X,
    DEFAULT_RESOLUTION_Y,
)
from scripts.utils import (
    create_material,
    create_object,
    render_to_file,
    reset_to_factory,
    setup_camera,
    setup_render_settings,
)


def create_objects():
    """Create various geometric objects in the scene."""
    objects = []

    # Create a red cube
    red_mat = create_material(name="Red", color=COLOR_RED)
    cube = create_object(obj_type="CUBE", size=2, location=(0, 0, 1), material=red_mat)
    objects.append(cube)

    # Create a green metallic sphere
    green_mat = create_material(name="Green", color=COLOR_GREEN, metallic=0.9)
    sphere = create_object(obj_type="SPHERE", size=2, location=(3, 3, 1), material=green_mat)
    bpy.ops.object.shade_smooth()  # Smooth shading for sphere
    objects.append(sphere)

    # Create a blue cone
    blue_mat = create_material(name="Blue", color=COLOR_BLUE)
    cone = create_object(obj_type="CONE", size=2, location=(-3, -3, 1), material=blue_mat)
    objects.append(cone)

    return objects

def main():
    """Main function to create and render a simple scene."""
    output_path = os.path.join(os.path.dirname(__file__), "output", "demo_render.png")

    # Reset the scene
    reset_to_factory()

    # Setup render settings
    setup_render_settings(
        resolution_x=DEFAULT_RESOLUTION_X,
        resolution_y=DEFAULT_RESOLUTION_Y,
        resolution_percentage=50,  # Faster renders for demo
        use_transparent_bg=True
    )

    # Create camera
    setup_camera(location=(7, -7, 5), rotation=(0.9, 0, 0.8))

    # Create lighting (sun + fill)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0

    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 3))
    fill = bpy.context.active_object
    fill.data.energy = 2.0

    # Create floor with custom material
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor_mat = create_material(name="Floor", color=(0.8, 0.8, 0.9, 1.0), roughness=0.1)
    floor.data.materials.append(floor_mat)

    # Create scene objects
    create_objects()

    # Render the scene
    render_to_file(output_path)

    print("Demo completed successfully")

if __name__ == "__main__":
    main()
