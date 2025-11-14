#!/usr/bin/env python3
"""
Scene Asset Generator
---------------------
Generate 3D assets for a small game or application scene using Blender.

This script creates:
- Environment assets (ground, sky)
- Props (crate, barrel, lamp post)
- Character placeholder (simple capsule)
- Renders from multiple angles
"""
import os
import sys
from math import radians

import bpy

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.utils import (
    create_material,
    render_to_file,
    reset_to_factory,
    setup_camera,
    setup_render_settings,
)


def create_wooden_crate(location=(0, 0, 0.5), size=1.0):
    """Create a wooden crate prop."""
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    crate = bpy.context.active_object
    crate.name = "Crate"

    # Wood material
    wood_mat = create_material(
        name="Wood",
        color=(0.4, 0.25, 0.1, 1.0),
        metallic=0.0,
        roughness=0.8
    )
    crate.data.materials.append(wood_mat)

    # Add bevel modifier for realism
    bevel = crate.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.02
    bevel.segments = 3

    return crate


def create_barrel(location=(0, 0, 0.5)):
    """Create a metal barrel prop."""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.0, location=location)
    barrel = bpy.context.active_object
    barrel.name = "Barrel"

    # Metal material
    metal_mat = create_material(
        name="Metal",
        color=(0.5, 0.5, 0.5, 1.0),
        metallic=0.9,
        roughness=0.3
    )
    barrel.data.materials.append(metal_mat)

    # Smooth shading
    bpy.ops.object.shade_smooth()

    return barrel


def create_lamp_post(location=(0, 0, 0)):
    """Create a lamp post prop."""
    # Post (cylinder)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3.0, location=(location[0], location[1], 1.5))
    post = bpy.context.active_object
    post.name = "LampPost"

    # Dark metal material
    dark_metal = create_material(
        name="DarkMetal",
        color=(0.1, 0.1, 0.1, 1.0),
        metallic=0.8,
        roughness=0.4
    )
    post.data.materials.append(dark_metal)

    # Lamp head (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(location[0], location[1], 3.2))
    lamp_head = bpy.context.active_object
    lamp_head.name = "LampHead"

    # Emissive material for lamp
    glow_mat = create_material(
        name="Glow",
        color=(1.0, 0.9, 0.7, 1.0),
        metallic=0.0,
        roughness=0.1
    )
    lamp_head.data.materials.append(glow_mat)

    # Add emission
    if glow_mat.use_nodes:
        nodes = glow_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        if principled:
            principled.inputs["Emission Color"].default_value = (1.0, 0.9, 0.7, 1.0)
            principled.inputs["Emission Strength"].default_value = 5.0

    # Add point light
    bpy.ops.object.light_add(type='POINT', location=(location[0], location[1], 3.2))
    light = bpy.context.active_object
    light.name = "LampLight"
    light.data.energy = 50
    light.data.color = (1.0, 0.9, 0.7)

    # Parent light to lamp head
    light.parent = lamp_head

    # Parent post and head together
    lamp_head.parent = post

    bpy.ops.object.shade_smooth()

    return post


def create_character_placeholder(location=(0, 0, 0)):
    """Create a simple character placeholder (capsule)."""
    # Body (cylinder)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.5, location=(location[0], location[1], 1.5))
    body = bpy.context.active_object
    body.name = "CharacterBody"

    # Head (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(location[0], location[1], 2.5))
    head = bpy.context.active_object
    head.name = "CharacterHead"

    # Character material
    char_mat = create_material(
        name="Character",
        color=(0.2, 0.4, 0.8, 1.0),
        metallic=0.0,
        roughness=0.6
    )
    body.data.materials.append(char_mat)
    head.data.materials.append(char_mat)

    # Parent head to body
    head.parent = body

    bpy.ops.object.shade_smooth()

    return body


def create_ground_plane(size=20):
    """Create ground with texture."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"

    # Ground material with subtle variation
    ground_mat = bpy.data.materials.new(name="Ground")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes
    links = ground_mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create noise texture for variation
    noise_tex = nodes.new(type="ShaderNodeTexNoise")
    noise_tex.inputs["Scale"].default_value = 3.0
    noise_tex.inputs["Detail"].default_value = 5.0

    # Color ramp for ground colors
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[0].color = (0.15, 0.12, 0.1, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.6
    color_ramp.color_ramp.elements[1].color = (0.2, 0.18, 0.15, 1.0)

    # Principled BSDF
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled.inputs["Roughness"].default_value = 0.95

    # Output
    output = nodes.new(type="ShaderNodeOutputMaterial")

    # Connect nodes
    links.new(noise_tex.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    ground.data.materials.append(ground_mat)

    return ground


def setup_scene_lighting():
    """Set up atmospheric lighting."""
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3.0
    sun.rotation_euler = (radians(50), radians(20), radians(30))
    sun.data.color = (1.0, 0.95, 0.9)

    # Ambient sky
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clear existing
    nodes.clear()

    # Sky texture
    sky_tex = nodes.new(type="ShaderNodeTexSky")
    sky_tex.sky_type = 'HOSEK_WILKIE'
    sky_tex.sun_elevation = radians(40)
    sky_tex.sun_rotation = radians(30)

    # Background
    bg = nodes.new(type="ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.8

    # Output
    output = nodes.new(type="ShaderNodeOutputWorld")

    # Connect
    links.new(sky_tex.outputs["Color"], bg.inputs["Color"])
    links.new(bg.outputs["Background"], output.inputs["Surface"])

    return sun


def create_scene():
    """Create the complete scene with all assets."""
    print("Creating scene assets...")

    # Reset Blender
    reset_to_factory()

    # Render settings
    setup_render_settings(
        engine="CYCLES",
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=100,
        samples=256
    )

    # Ground
    create_ground_plane(size=30)

    # Lighting
    setup_scene_lighting()

    # Assets in scene
    create_wooden_crate(location=(-2, 1, 0.5), size=1.0)
    create_wooden_crate(location=(-2, -1, 0.5), size=0.8)
    create_barrel(location=(2, -2, 0.5))
    create_barrel(location=(3, -1.5, 0.5))
    create_lamp_post(location=(4, 3, 0))
    create_lamp_post(location=(-4, 3, 0))

    # Character
    character = create_character_placeholder(location=(0, 0, 0.75))
    character.rotation_euler = (0, 0, radians(45))

    print("Scene assets created!")


def render_scene_angles(output_dir):
    """Render the scene from multiple camera angles."""
    os.makedirs(output_dir, exist_ok=True)

    # Camera angle 1: Wide shot
    print("Rendering wide shot...")
    cam1 = setup_camera(
        location=(8, -8, 4),
        rotation=(radians(65), 0, radians(45)),
        lens=35
    )
    render_to_file(os.path.join(output_dir, "scene_wide.png"))

    # Camera angle 2: Close-up on character
    print("Rendering character close-up...")
    cam1.location = (2, -3, 2)
    cam1.rotation_euler = (radians(80), 0, radians(30))
    cam1.data.lens = 50
    render_to_file(os.path.join(output_dir, "scene_character.png"))

    # Camera angle 3: Top-down view
    print("Rendering top-down view...")
    cam1.location = (0, 0, 15)
    cam1.rotation_euler = (0, 0, 0)
    cam1.data.lens = 35
    render_to_file(os.path.join(output_dir, "scene_topdown.png"))

    # Camera angle 4: Props detail
    print("Rendering props detail...")
    cam1.location = (1, -4, 1.5)
    cam1.rotation_euler = (radians(85), 0, radians(15))
    cam1.data.lens = 75
    render_to_file(os.path.join(output_dir, "scene_props.png"))

    print(f"All renders saved to: {output_dir}")


def save_blend_file(output_dir):
    """Save the scene as a .blend file."""
    blend_path = os.path.join(output_dir, "scene_assets.blend")
    os.makedirs(output_dir, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Scene saved to: {blend_path}")


def main():
    """Main function to generate scene assets."""
    output_dir = os.path.join(os.path.dirname(__file__), "output", "scene_assets")

    print("=" * 60)
    print("Scene Asset Generator - Blender Wheel Demo")
    print("=" * 60)

    # Create the scene
    create_scene()

    # Save .blend file
    save_blend_file(output_dir)

    # Render from multiple angles
    render_scene_angles(output_dir)

    print("=" * 60)
    print("Asset generation complete!")
    print(f"Output directory: {output_dir}")
    print("Generated files:")
    print("  - scene_assets.blend (Blender scene file)")
    print("  - scene_wide.png (Wide shot render)")
    print("  - scene_character.png (Character close-up)")
    print("  - scene_topdown.png (Top-down view)")
    print("  - scene_props.png (Props detail)")
    print("=" * 60)


if __name__ == "__main__":
    main()
