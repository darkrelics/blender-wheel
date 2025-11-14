#!/usr/bin/env python3
"""
Blender Animation Demo Script
----------------------------
Creates a simple animated scene with keyframed objects.
"""
import os
import sys
from math import cos, pi, radians, sin

import bpy

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.constants import (
    DEFAULT_FRAME_END,
    DEFAULT_FRAME_START,
    DEFAULT_SAMPLES_PREVIEW,
)
from scripts.utils import reset_to_factory, setup_render_settings


def setup_environment():
    """Setup camera, lights, and environment."""
    # Create camera
    bpy.ops.object.camera_add(location=(0, -12, 5))
    camera = bpy.context.active_object
    camera.name = "Main Camera"
    camera.rotation_euler = (radians(65), 0, 0)
    bpy.context.scene.camera = camera

    # Create key light
    bpy.ops.object.light_add(type="AREA", location=(6, -6, 8))
    key_light = bpy.context.active_object
    key_light.name = "Key Light"
    key_light.data.energy = 500
    key_light.data.size = 2

    # Create fill light
    bpy.ops.object.light_add(type="AREA", location=(-6, -6, 8))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill Light"
    fill_light.data.energy = 200
    fill_light.data.size = 2

    # Rim light
    bpy.ops.object.light_add(type="AREA", location=(0, 6, 4))
    rim_light = bpy.context.active_object
    rim_light.name = "Rim Light"
    rim_light.data.energy = 300
    rim_light.data.size = 1

    # Create a world environment
    world = bpy.context.scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes

    # Clear existing nodes
    for node in world_nodes:
        world_nodes.remove(node)

    # Create a sky texture
    bg_node = world_nodes.new(type="ShaderNodeBackground")
    bg_node.inputs["Color"].default_value = (0.05, 0.05, 0.08, 1.0)
    bg_node.inputs["Strength"].default_value = 1.0

    output_node = world_nodes.new(type="ShaderNodeOutputWorld")

    # Link nodes
    links = world.node_tree.links
    links.new(bg_node.outputs["Background"], output_node.inputs["Surface"])

    # Create a ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "Ground"

    # Add a simple material to the ground
    ground_mat = bpy.data.materials.new(name="Ground")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
        principled_bsdf.inputs["Roughness"].default_value = 0.95

    plane.data.materials.append(ground_mat)


def create_material(name, color, metallic=0.0, roughness=0.5):
    """Create a material with the given properties."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
        principled_bsdf.inputs["Metallic"].default_value = metallic
        principled_bsdf.inputs["Roughness"].default_value = roughness

    return mat


def create_bouncing_sphere():
    """Create a sphere that bounces up and down."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
    sphere = bpy.context.active_object
    sphere.name = "Bouncing Sphere"

    # Smooth the sphere
    bpy.ops.object.shade_smooth()

    # Add material
    mat = create_material("Red Material", (0.8, 0.1, 0.1, 1.0), metallic=0.0, roughness=0.2)
    sphere.data.materials.append(mat)

    # Set starting keyframe at frame 1
    bpy.context.scene.frame_set(1)
    sphere.location = (0, 0, 1)
    sphere.keyframe_insert(data_path="location", index=2)

    # Set highest point at frame 30
    bpy.context.scene.frame_set(30)
    sphere.location = (0, 0, 5)
    sphere.keyframe_insert(data_path="location", index=2)

    # Set lowest point at frame 60
    bpy.context.scene.frame_set(60)
    sphere.location = (0, 0, 1)
    sphere.keyframe_insert(data_path="location", index=2)

    # Set highest point at frame 90
    bpy.context.scene.frame_set(90)
    sphere.location = (0, 0, 5)
    sphere.keyframe_insert(data_path="location", index=2)

    # Set lowest point at frame 120
    bpy.context.scene.frame_set(120)
    sphere.location = (0, 0, 1)
    sphere.keyframe_insert(data_path="location", index=2)

    # Set interpolation to bounce
    for fc in sphere.animation_data.action.fcurves:
        for kf in fc.keyframe_points:
            kf.interpolation = "BOUNCE"

    return sphere


def create_orbiting_cube():
    """Create a cube that orbits around the scene."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 0, 1.5))
    cube = bpy.context.active_object
    cube.name = "Orbiting Cube"

    # Add material
    mat = create_material("Blue Material", (0.1, 0.3, 0.8, 1.0), metallic=0.8, roughness=0.2)
    cube.data.materials.append(mat)

    # Create a path of keyframes for orbit
    frames = 120
    radius = 5

    for frame in range(1, frames + 1):
        # Set the frame
        bpy.context.scene.frame_set(frame)

        # Calculate position based on circle
        angle = 2 * pi * frame / frames
        x = radius * cos(angle)
        y = radius * sin(angle)

        # Set position
        cube.location = (x, y, 1.5)

        # Insert keyframe
        cube.keyframe_insert(data_path="location")

        # Add rotation for interest
        cube.rotation_euler = (frame * 0.1, frame * 0.1, angle)
        cube.keyframe_insert(data_path="rotation_euler")

    # Smooth the animation
    for fc in cube.animation_data.action.fcurves:
        for kf in fc.keyframe_points:
            kf.interpolation = "LINEAR"

    return cube


def create_scaling_cone():
    """Create a cone that scales up and down."""
    bpy.ops.mesh.primitive_cone_add(radius1=1, location=(0, -4, 1), depth=2)
    cone = bpy.context.active_object
    cone.name = "Scaling Cone"

    # Add material
    mat = create_material("Green Material", (0.1, 0.8, 0.2, 1.0), metallic=0.0, roughness=0.5)
    cone.data.materials.append(mat)

    # Initial scale keyframe
    bpy.context.scene.frame_set(1)
    cone.scale = (1, 1, 1)
    cone.keyframe_insert(data_path="scale")

    # Scale up keyframe
    bpy.context.scene.frame_set(40)
    cone.scale = (2, 2, 0.5)
    cone.keyframe_insert(data_path="scale")

    # Scale differently keyframe
    bpy.context.scene.frame_set(80)
    cone.scale = (0.5, 0.5, 2)
    cone.keyframe_insert(data_path="scale")

    # Return to original scale
    bpy.context.scene.frame_set(120)
    cone.scale = (1, 1, 1)
    cone.keyframe_insert(data_path="scale")

    # Smooth the animation
    for fc in cone.animation_data.action.fcurves:
        for kf in fc.keyframe_points:
            kf.interpolation = "ELASTIC"

    return cone


def animate_camera():
    """Add slight camera movement for interest."""
    camera = bpy.data.objects["Main Camera"]

    # Initial position
    bpy.context.scene.frame_set(1)
    camera.location = (0, -12, 5)
    camera.rotation_euler = (radians(65), 0, 0)
    camera.keyframe_insert(data_path="location")
    camera.keyframe_insert(data_path="rotation_euler")

    # Move to new position
    bpy.context.scene.frame_set(60)
    camera.location = (3, -11, 5)
    camera.rotation_euler = (radians(65), radians(15), 0)
    camera.keyframe_insert(data_path="location")
    camera.keyframe_insert(data_path="rotation_euler")

    # Move to final position
    bpy.context.scene.frame_set(120)
    camera.location = (-3, -11, 5)
    camera.rotation_euler = (radians(65), radians(-15), 0)
    camera.keyframe_insert(data_path="location")
    camera.keyframe_insert(data_path="rotation_euler")

    # Smooth the animation
    for fc in camera.animation_data.action.fcurves:
        for kf in fc.keyframe_points:
            kf.interpolation = "BEZIER"


def render_animation(output_path):
    """Render the animation to a folder of frames."""
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Set render settings
    bpy.context.scene.render.filepath = os.path.join(output_path, "frame_")
    bpy.context.scene.render.image_settings.file_format = "PNG"

    print(f"Animation will be rendered to: {output_path}")
    print("Note: In a real scenario, you would use:")
    print("bpy.ops.render.render(animation=True)")
    print("But this may take a long time, so we're just setting up the animation.")

    # For the demo, we'll just render a single frame
    # In a real scenario, you would uncomment the following line:
    # bpy.ops.render.render(animation=True)

    # Just render the first frame for the demo
    bpy.context.scene.frame_set(1)
    bpy.ops.render.render(write_still=True)

    print(f"First frame rendered as a preview to: {bpy.context.scene.render.filepath}001.png")


def main():
    """Main function to create and set up the animation."""
    output_path = os.path.join(os.path.dirname(__file__), "output", "animation")

    # Reset the scene
    reset_to_factory()

    # Setup render settings for animation
    setup_render_settings(
        resolution_x=1280,
        resolution_y=720,
        resolution_percentage=50,
        samples=DEFAULT_SAMPLES_PREVIEW  # Lower samples for faster animation renders
    )

    # Set frame range
    bpy.context.scene.frame_start = DEFAULT_FRAME_START
    bpy.context.scene.frame_end = DEFAULT_FRAME_END
    bpy.context.scene.render.fps = 30

    # Setup environment
    setup_environment()

    # Create animated objects
    create_bouncing_sphere()
    create_orbiting_cube()
    create_scaling_cone()

    # Animate camera
    animate_camera()

    # Render preview frame
    render_animation(output_path)

    print("Animation demo completed successfully")
    print("To render the full animation, uncomment the render line in the render_animation function")


if __name__ == "__main__":
    main()
