#!/usr/bin/env python3
"""
Basic Blender Demo Script
-------------------------
Creates a simple 3D scene with geometric primitives and renders it.
"""
import os

import bpy

def reset_scene():
    """Clear the current scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Remove default objects
    if 'Cube' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Cube'])
    
    # Set render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 50  # faster renders for demo

def create_camera():
    """Create and position the camera."""
    bpy.ops.object.camera_add(location=(7, -7, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (0.9, 0, 0.8)
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    return camera

def create_light():
    """Create a key light."""
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.active_object
    light.data.energy = 5.0
    
    # Add a second, fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 3))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 2.0
    
    return light

def create_floor():
    """Create a floor plane."""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    floor = bpy.context.active_object
    
    # Add a simple material
    mat = bpy.data.materials.new(name="Floor")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Color the floor slightly blue-grey
    principled_bsdf = nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.9, 1.0)
        principled_bsdf.inputs['Roughness'].default_value = 0.1
    
    floor.data.materials.append(mat)
    
    return floor

def create_objects():
    """Create various geometric objects in the scene."""
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    cube = bpy.context.active_object
    
    # Create a material
    mat = bpy.data.materials.new(name="Red")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Make it red
    principled_bsdf = nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.2, 1.0)
    
    cube.data.materials.append(mat)
    
    # Create a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 3, 1))
    sphere = bpy.context.active_object
    
    # Create a material
    mat = bpy.data.materials.new(name="Green")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Make it green
    principled_bsdf = nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)
        principled_bsdf.inputs['Metallic'].default_value = 0.9
    
    sphere.data.materials.append(mat)
    
    # Create a cone
    bpy.ops.mesh.primitive_cone_add(radius1=1, location=(-3, -3, 1), depth=2)
    cone = bpy.context.active_object
    
    # Create a material
    mat = bpy.data.materials.new(name="Blue")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Make it blue
    principled_bsdf = nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.8, 1.0)
    
    cone.data.materials.append(mat)
    
    return [cube, sphere, cone]

def render_scene(output_path):
    """Render the scene to an image file."""
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Set render settings
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    
    # Render the scene
    bpy.ops.render.render(write_still=True)
    
    print(f"Rendered image saved to: {output_path}")

def main():
    """Main function to create and render a simple scene."""
    output_path = os.path.join(os.path.dirname(__file__), "output", "demo_render.png")
    
    # Reset the scene
    reset_scene()
    
    # Create scene elements
    create_camera()
    create_light()
    create_floor()
    create_objects()
    
    # Render the scene
    render_scene(output_path)
    
    print("Demo completed successfully")

if __name__ == "__main__":
    main()