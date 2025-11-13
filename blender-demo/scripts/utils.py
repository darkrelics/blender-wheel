#!/usr/bin/env python3
"""
Blender Python utilities
-----------------------
Common helper functions for working with Blender in Python.
"""
import os
import math
from math import radians

import bpy


def reset_to_factory():
    """Reset Blender to factory settings and remove default objects."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Remove default objects
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"])

    # Set default render settings
    bpy.context.scene.render.engine = "CYCLES"

    return True


def setup_render_settings(
    engine="CYCLES", resolution_x=1920, resolution_y=1080, resolution_percentage=100, samples=128, use_transparent_bg=False
):
    """Set up render settings."""
    bpy.context.scene.render.engine = engine
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    bpy.context.scene.render.resolution_percentage = resolution_percentage

    if engine == "CYCLES":
        bpy.context.scene.cycles.samples = samples

    bpy.context.scene.render.film_transparent = use_transparent_bg

    return True


def setup_camera(location=(0, -10, 5), rotation=(radians(60), 0, 0), lens=35, clip_start=0.1, clip_end=100):
    """Create and set up a camera."""
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.rotation_euler = rotation

    # Set camera parameters
    camera.data.lens = lens
    camera.data.clip_start = clip_start
    camera.data.clip_end = clip_end

    # Make this the active camera
    bpy.context.scene.camera = camera

    return camera


def setup_lighting(light_setup="three_point"):
    """Set up common lighting setups."""
    lights = []

    if light_setup == "three_point":
        # Key light
        bpy.ops.object.light_add(type="AREA", location=(5, -5, 5))
        key_light = bpy.context.active_object
        key_light.name = "Key Light"
        key_light.data.energy = 500
        key_light.data.size = 2
        lights.append(key_light)

        # Fill light
        bpy.ops.object.light_add(type="AREA", location=(-5, -3, 3))
        fill_light = bpy.context.active_object
        fill_light.name = "Fill Light"
        fill_light.data.energy = 200
        fill_light.data.size = 2
        lights.append(fill_light)

        # Back light
        bpy.ops.object.light_add(type="AREA", location=(0, 7, 4))
        back_light = bpy.context.active_object
        back_light.name = "Back Light"
        back_light.data.energy = 300
        back_light.data.size = 1
        lights.append(back_light)

    elif light_setup == "studio":
        # Main light
        bpy.ops.object.light_add(type="AREA", location=(0, -5, 5))
        main_light = bpy.context.active_object
        main_light.name = "Main Light"
        main_light.data.energy = 800
        main_light.data.size = 4
        main_light.data.size_y = 3
        lights.append(main_light)

        # Fill lights
        for i in range(3):
            angle = (i * 120) + 30
            x = 6 * math.cos(math.radians(angle))
            y = 6 * math.sin(math.radians(angle))

            bpy.ops.object.light_add(type="AREA", location=(x, y, 2))
            fill = bpy.context.active_object
            fill.name = f"Fill Light {i+1}"
            fill.data.energy = 200
            fill.data.size = 2
            lights.append(fill)

    elif light_setup == "outdoor":
        # Sun
        bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
        sun = bpy.context.active_object
        sun.name = "Sun"
        sun.data.energy = 5
        sun.rotation_euler = (radians(60), 0, radians(30))
        lights.append(sun)

        # Ambient fill
        bpy.ops.object.light_add(type="AREA", location=(0, 0, 5))
        ambient = bpy.context.active_object
        ambient.name = "Ambient Fill"
        ambient.data.energy = 0.3
        ambient.data.size = 10
        lights.append(ambient)

    return lights


def create_ground_plane(size=20, location=(0, 0, 0), color=(0.2, 0.2, 0.2, 1.0), roughness=0.9):
    """Create a ground plane with material."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    plane = bpy.context.active_object
    plane.name = "Ground Plane"

    # Add material
    mat = bpy.data.materials.new(name="Ground Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
        principled_bsdf.inputs["Roughness"].default_value = roughness

    plane.data.materials.append(mat)

    return plane


def create_material(
    name="New Material", color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.5, specular=0.5, transmission=0.0, ior=1.45
):
    """Create a material with specified properties."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled_bsdf = nodes.get("Principled BSDF")
    if principled_bsdf:
        principled_bsdf.inputs["Base Color"].default_value = color
        principled_bsdf.inputs["Metallic"].default_value = metallic
        principled_bsdf.inputs["Roughness"].default_value = roughness
        principled_bsdf.inputs["Specular"].default_value = specular
        principled_bsdf.inputs["Transmission"].default_value = transmission
        principled_bsdf.inputs["IOR"].default_value = ior

    return mat


def create_object(obj_type="CUBE", size=1, location=(0, 0, 0), rotation=(0, 0, 0), material=None):
    """Create an object of the specified type."""
    if obj_type == "CUBE":
        bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=rotation)
    elif obj_type == "SPHERE":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size / 2, location=location)
    elif obj_type == "CYLINDER":
        bpy.ops.mesh.primitive_cylinder_add(radius=size / 2, depth=size, location=location)
    elif obj_type == "CONE":
        bpy.ops.mesh.primitive_cone_add(radius1=size / 2, depth=size, location=location)
    elif obj_type == "TORUS":
        bpy.ops.mesh.primitive_torus_add(major_radius=size / 2, minor_radius=size / 4, location=location)
    else:
        raise ValueError(f"Unknown object type: {obj_type}")

    obj = bpy.context.active_object

    # Assign material if provided
    if material is not None:
        obj.data.materials.append(material)

    return obj


def apply_modifiers(obj, modifiers_dict):
    """Apply modifiers to an object.

    Args:
        obj: Blender object to apply modifiers to
        modifiers_dict: Dictionary of modifiers and their parameters

    Example:
        modifiers = {
            'SUBSURF': {'levels': 2},
            'BEVEL': {'width': 0.1, 'segments': 3}
        }
        apply_modifiers(my_object, modifiers)
    """
    for mod_type, params in modifiers_dict.items():
        mod = obj.modifiers.new(name=mod_type, type=mod_type)

        for param, value in params.items():
            setattr(mod, param, value)

    return obj


def save_file(filepath):
    """Save the current Blender file.

    Args:
        filepath: Path where to save the .blend file

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If filepath is invalid
        OSError: If directory cannot be created or file cannot be saved
    """
    if not filepath:
        raise ValueError("filepath cannot be empty")

    # Ensure directory exists
    directory = os.path.dirname(filepath)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory {directory}: {e}")

    # Save file
    try:
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
    except Exception as e:
        raise OSError(f"Failed to save file {filepath}: {e}")

    # Verify file was created
    if not os.path.exists(filepath):
        raise OSError(f"File was not created at {filepath}")

    return True


def render_to_file(output_path, file_format="PNG"):
    """Render the current scene to a file.

    Args:
        output_path: Path where to save the rendered image
        file_format: Image format (PNG, JPEG, etc.)

    Returns:
        True if successful

    Raises:
        ValueError: If output_path is invalid or file_format unsupported
        OSError: If directory cannot be created
        RuntimeError: If rendering fails
    """
    if not output_path:
        raise ValueError("output_path cannot be empty")

    valid_formats = ['PNG', 'JPEG', 'BMP', 'TIFF', 'OPEN_EXR', 'HDR']
    if file_format not in valid_formats:
        raise ValueError(f"Invalid file_format '{file_format}'. Must be one of: {valid_formats}")

    # Ensure directory exists
    directory = os.path.dirname(output_path)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory {directory}: {e}")

    # Set render settings
    try:
        bpy.context.scene.render.filepath = output_path
        bpy.context.scene.render.image_settings.file_format = file_format
    except Exception as e:
        raise ValueError(f"Failed to set render settings: {e}")

    # Render
    try:
        bpy.ops.render.render(write_still=True)
    except Exception as e:
        raise RuntimeError(f"Rendering failed: {e}")

    # Verify output was created
    if not os.path.exists(output_path):
        raise RuntimeError(f"Render output was not created at {output_path}")

    return True


def animate_property(obj, property_path, start_frame, end_frame, start_value, end_value, interpolation="BEZIER"):
    """Animate a property from start_value to end_value over frame range."""
    # Set start keyframe
    bpy.context.scene.frame_set(start_frame)

    # Convert property_path to attribute access
    attrs = property_path.split(".")
    prop_obj = obj

    # Navigate through object attributes to find the right property
    for attr in attrs[:-1]:
        if hasattr(prop_obj, attr):
            prop_obj = getattr(prop_obj, attr)
        else:
            raise AttributeError(f"Object does not have attribute {attr}")

    # Set property at start frame
    final_attr = attrs[-1]
    setattr(prop_obj, final_attr, start_value)

    # Set keyframe
    if isinstance(obj, bpy.types.Object):
        obj.keyframe_insert(data_path=property_path)
    else:
        # For non-Object types, insert keyframe differently
        prop_obj.keyframe_insert(final_attr)

    # Set end keyframe
    bpy.context.scene.frame_set(end_frame)
    setattr(prop_obj, final_attr, end_value)

    # Set keyframe
    if isinstance(obj, bpy.types.Object):
        obj.keyframe_insert(data_path=property_path)
    else:
        prop_obj.keyframe_insert(final_attr)

    # Set interpolation
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            if fc.data_path == property_path:
                for kf in fc.keyframe_points:
                    kf.interpolation = interpolation

    return True


def get_object_by_name(name):
    """Get a Blender object by name."""
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    return None


def set_scene_frame(frame):
    """Set the current scene frame."""
    bpy.context.scene.frame_set(frame)
    return True
