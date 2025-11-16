#!/usr/bin/env python3
"""
Blender Materials Demo Script
----------------------------
Demonstrates creating various materials and textures in Blender.

Usage:
    Run from the blender-demo directory:
        cd blender-demo
        python materials_demo.py

    Or specify PYTHONPATH:
        PYTHONPATH=blender-demo python blender-demo/materials_demo.py
"""
import os
from math import radians

import bpy
import numpy as np

# Import from scripts module (works when running from blender-demo directory)
from scripts.constants import (
    DEFAULT_RESOLUTION_X,
    DEFAULT_RESOLUTION_Y,
    DEFAULT_SAMPLES,
)
from scripts.utils import reset_to_factory, setup_render_settings


def setup_environment():
    """Setup camera, lights, and environment."""
    # Create camera
    bpy.ops.object.camera_add(location=(0, -16, 4))
    camera = bpy.context.active_object
    camera.rotation_euler = (radians(75), 0, 0)
    bpy.context.scene.camera = camera

    # Create key light
    bpy.ops.object.light_add(type="AREA", location=(6, -6, 8))
    key_light = bpy.context.active_object
    key_light.data.energy = 500
    key_light.data.size = 2

    # Create fill light
    bpy.ops.object.light_add(type="AREA", location=(-6, -6, 8))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 200
    fill_light.data.size = 2

    # Create a world environment
    world = bpy.context.scene.world
    world.use_nodes = True
    world_nodes = world.node_tree.nodes

    # Clear existing nodes
    for node in world_nodes:
        world_nodes.remove(node)

    # Create a sky texture
    bg_node = world_nodes.new(type="ShaderNodeBackground")
    bg_node.inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)
    bg_node.inputs["Strength"].default_value = 1.0

    output_node = world_nodes.new(type="ShaderNodeOutputWorld")

    # Link nodes
    links = world.node_tree.links
    links.new(bg_node.outputs["Background"], output_node.inputs["Surface"])

    # Create a ground plane
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -2))
    plane = bpy.context.active_object

    # Add a simple material to the ground
    ground_mat = bpy.data.materials.new(name="Ground")
    ground_mat.use_nodes = True
    nodes = ground_mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
        principled_bsdf.inputs["Roughness"].default_value = 0.95

    plane.data.materials.append(ground_mat)


def create_sphere(location, index):
    """Create a sphere at the specified location."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=location, segments=32, ring_count=16)
    sphere = bpy.context.active_object

    # Smooth the sphere
    bpy.ops.object.shade_smooth()

    return sphere


def create_metal_material(name, color, roughness, metallic):
    """Create a metal-like material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
        principled_bsdf.inputs["Metallic"].default_value = metallic
        principled_bsdf.inputs["Roughness"].default_value = roughness
        principled_bsdf.inputs["Specular"].default_value = 0.5

    return mat


def create_glass_material(name, color, roughness, ior):
    """Create a glass-like material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)

    # Create glass shader
    glass_node = nodes.new(type="ShaderNodeBsdfGlass")
    glass_node.inputs["Color"].default_value = color
    glass_node.inputs["Roughness"].default_value = roughness
    glass_node.inputs["IOR"].default_value = ior

    output_node = nodes.new(type="ShaderNodeOutputMaterial")

    # Link nodes
    links.new(glass_node.outputs["BSDF"], output_node.inputs["Surface"])

    return mat


def create_procedural_material(name):
    """Create a procedurally textured material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    for node in nodes:
        nodes.remove(node)

    # Create noise texture
    noise_tex = nodes.new(type="ShaderNodeTexNoise")
    noise_tex.inputs["Scale"].default_value = 5.0
    noise_tex.inputs["Detail"].default_value = 8.0
    noise_tex.inputs["Roughness"].default_value = 0.7

    # Create color ramp
    color_ramp = nodes.new(type="ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = (0.0, 0.1, 0.6, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.7
    color_ramp.color_ramp.elements[1].color = (0.6, 0.0, 0.3, 1.0)

    # Add a new element
    new_element = color_ramp.color_ramp.elements.new(0.5)
    new_element.color = (0.3, 0.0, 0.6, 1.0)

    # Create principled BSDF shader
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled.inputs["Roughness"].default_value = 0.3
    principled.inputs["Metallic"].default_value = 0.7

    # Create bump node
    bump_node = nodes.new(type="ShaderNodeBump")
    bump_node.inputs["Strength"].default_value = 0.5

    # Create output
    output = nodes.new(type="ShaderNodeOutputMaterial")

    # Link nodes
    links.new(noise_tex.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], principled.inputs["Base Color"])
    links.new(noise_tex.outputs["Fac"], bump_node.inputs["Height"])
    links.new(bump_node.outputs["Normal"], principled.inputs["Normal"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    return mat


def create_subsurface_material(name, color, subsurface):
    """Create a material with subsurface scattering."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
        principled_bsdf.inputs["Subsurface"].default_value = subsurface
        principled_bsdf.inputs["Subsurface Color"].default_value = (0.9, 0.3, 0.3, 1.0)
        principled_bsdf.inputs["Roughness"].default_value = 0.3

    return mat


def create_material_samples():
    """Create a grid of spheres with different materials."""
    grid_size = 4
    spacing = 3

    # Initialize counters
    sphere_index = 0
    materials = []

    # Create a grid of spheres
    for i in range(grid_size):
        for j in range(grid_size):
            x = (i - grid_size / 2 + 0.5) * spacing
            y = (j - grid_size / 2 + 0.5) * spacing

            sphere = create_sphere((x, y, 0), sphere_index)
            sphere_index += 1

            # Create a unique material for each sphere
            if i == 0 and j == 0:
                # Metal - Gold
                mat = create_metal_material("Gold", (1.0, 0.8, 0.0, 1.0), 0.1, 1.0)
            elif i == 0 and j == 1:
                # Metal - Silver
                mat = create_metal_material("Silver", (0.9, 0.9, 0.9, 1.0), 0.1, 1.0)
            elif i == 0 and j == 2:
                # Metal - Copper
                mat = create_metal_material("Copper", (0.8, 0.5, 0.2, 1.0), 0.15, 1.0)
            elif i == 0 and j == 3:
                # Brushed Metal
                mat = create_metal_material("Brushed Metal", (0.7, 0.7, 0.7, 1.0), 0.4, 1.0)
            elif i == 1 and j == 0:
                # Glass - Clear
                mat = create_glass_material("Clear Glass", (1.0, 1.0, 1.0, 1.0), 0.0, 1.45)
            elif i == 1 and j == 1:
                # Glass - Blue
                mat = create_glass_material("Blue Glass", (0.1, 0.3, 0.8, 1.0), 0.05, 1.45)
            elif i == 1 and j == 2:
                # Glass - Rough
                mat = create_glass_material("Rough Glass", (0.8, 0.8, 0.8, 1.0), 0.3, 1.45)
            elif i == 1 and j == 3:
                # Frosted Glass
                mat = create_glass_material("Frosted Glass", (0.9, 0.9, 0.9, 1.0), 0.5, 1.45)
            elif i == 2 and j == 0:
                # Plastic - Red
                mat = create_metal_material("Red Plastic", (0.8, 0.0, 0.0, 1.0), 0.3, 0.0)
            elif i == 2 and j == 1:
                # Plastic - Green
                mat = create_metal_material("Green Plastic", (0.0, 0.8, 0.0, 1.0), 0.3, 0.0)
            elif i == 2 and j == 2:
                # Plastic - Blue
                mat = create_metal_material("Blue Plastic", (0.0, 0.0, 0.8, 1.0), 0.3, 0.0)
            elif i == 2 and j == 3:
                # Rubber
                mat = create_metal_material("Rubber", (0.02, 0.02, 0.02, 1.0), 0.9, 0.0)
            elif i == 3 and j == 0:
                # Wax - Subsurface
                mat = create_subsurface_material("Wax", (0.9, 0.8, 0.5, 1.0), 0.7)
            elif i == 3 and j == 1:
                # Skin - Subsurface
                mat = create_subsurface_material("Skin", (0.8, 0.5, 0.4, 1.0), 0.4)
            elif i == 3 and j == 2:
                # Marble - Procedural
                mat = create_procedural_material("Marble")
            else:
                # Default material
                mat = create_metal_material(
                    f"Material_{sphere_index}",
                    (np.random.random(), np.random.random(), np.random.random(), 1.0),
                    np.random.random(),
                    np.random.random(),
                )

            materials.append(mat)
            sphere.data.materials.append(mat)


def render_scene(output_path):
    """Render the scene to an image file."""
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Set render settings
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = "PNG"

    # Render the scene
    bpy.ops.render.render(write_still=True)

    print(f"Rendered image saved to: {output_path}")


def main():
    """Main function to create and render a materials showcase."""
    output_path = os.path.join(os.path.dirname(__file__), "output", "materials_demo.png")

    # Reset the scene
    reset_to_factory()

    # Setup render settings
    setup_render_settings(
        resolution_x=DEFAULT_RESOLUTION_X,
        resolution_y=DEFAULT_RESOLUTION_Y,
        resolution_percentage=50,  # Faster preview
        samples=DEFAULT_SAMPLES
    )

    # Setup environment
    setup_environment()

    # Create material samples
    create_material_samples()

    # Render the scene
    render_scene(output_path)

    print("Materials demo completed successfully")


if __name__ == "__main__":
    main()
