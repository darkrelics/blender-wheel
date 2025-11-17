#!/usr/bin/env python3
"""
Blender Batch Rendering Script
----------------------------
Renders multiple scenes with different settings.
"""
import argparse
import datetime
import json
import logging
import os
import sys

import bpy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.constants import (
    DEFAULT_RESOLUTION_X,
    DEFAULT_RESOLUTION_Y,
    DEFAULT_SAMPLES,
    DEFAULT_SAMPLES_PREVIEW,
)
from scripts.utils import (
    create_ground_plane,
    create_material,
    create_object,
    render_to_file,
    reset_to_factory,
    setup_camera,
    setup_lighting,
    setup_render_settings,
)


def create_scene(scene_data):
    """
    Create a scene based on scene data dictionary.

    Args:
        scene_data: Dictionary with scene configuration

    Returns:
        True if successful
    """
    # Reset Blender
    reset_to_factory()

    # Setup render settings
    setup_render_settings(
        engine=scene_data.get("render_engine", "CYCLES"),
        resolution_x=scene_data.get("resolution_x", DEFAULT_RESOLUTION_X),
        resolution_y=scene_data.get("resolution_y", DEFAULT_RESOLUTION_Y),
        resolution_percentage=scene_data.get("resolution_percentage", 50),
        samples=scene_data.get("samples", DEFAULT_SAMPLES_PREVIEW),
        use_transparent_bg=scene_data.get("transparent_background", False),
    )

    # Setup camera
    camera_data = scene_data.get("camera", {})
    camera = setup_camera(
        location=camera_data.get("location", (0, -10, 5)),
        rotation=camera_data.get("rotation", (1.0, 0, 0)),
        lens=camera_data.get("lens", 35),
    )

    # Setup lighting
    lighting_data = scene_data.get("lighting", {})
    lights = setup_lighting(lighting_data.get("setup", "three_point"))

    # Create ground plane if needed
    if scene_data.get("create_ground", True):
        ground_data = scene_data.get("ground", {})
        ground = create_ground_plane(
            size=ground_data.get("size", 20),
            location=ground_data.get("location", (0, 0, 0)),
            color=ground_data.get("color", (0.2, 0.2, 0.2, 1.0)),
            roughness=ground_data.get("roughness", 0.9),
        )

    # Create objects
    objects = []
    for obj_data in scene_data.get("objects", []):
        # Create material first if specified
        material = None
        if "material" in obj_data:
            mat_data = obj_data["material"]
            material = create_material(
                name=mat_data.get("name", "Object Material"),
                color=mat_data.get("color", (0.8, 0.8, 0.8, 1.0)),
                metallic=mat_data.get("metallic", 0.0),
                roughness=mat_data.get("roughness", 0.5),
                specular=mat_data.get("specular", 0.5),
                transmission=mat_data.get("transmission", 0.0),
                ior=mat_data.get("ior", 1.45),
            )

        # Create object
        obj = create_object(
            obj_type=obj_data.get("type", "CUBE"),
            size=obj_data.get("size", 1),
            location=obj_data.get("location", (0, 0, 0)),
            rotation=obj_data.get("rotation", (0, 0, 0)),
            material=material,
        )

        # Apply smooth shading to spheres
        if obj_data.get("type") == "SPHERE":
            bpy.ops.object.shade_smooth()

        objects.append(obj)

    return True


def render_scenes_from_config(config_file, output_dir):
    """
    Render multiple scenes from a configuration file.

    Args:
        config_file: Path to JSON configuration file
        output_dir: Directory to save renders

    Returns:
        List of paths to rendered images
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load configuration
    with open(config_file) as f:
        config = json.load(f)

    rendered_files = []

    # Process each scene
    for i, scene_data in enumerate(config.get("scenes", [])):
        scene_name = scene_data.get("name", f"scene_{i+1}")
        logger.info(f"Rendering scene: {scene_name}")

        # Create the scene
        create_scene(scene_data)

        # Set the output path
        output_path = os.path.join(output_dir, f"{scene_name}.png")

        # Render
        render_to_file(output_path, file_format="PNG")

        rendered_files.append(output_path)
        logger.info(f"Rendered {scene_name} to {output_path}")

    return rendered_files


def create_sample_config(config_path):
    """
    Create a sample configuration file.

    Args:
        config_path: Path to save the configuration file
    """
    sample_config = {
        "scenes": [
            {
                "name": "red_cube",
                "render_engine": "CYCLES",
                "resolution_x": 1280,
                "resolution_y": 720,
                "resolution_percentage": 50,
                "samples": DEFAULT_SAMPLES_PREVIEW,
                "transparent_background": False,
                "camera": {"location": [0, -10, 5], "rotation": [1.0, 0, 0], "lens": 35},
                "lighting": {"setup": "three_point"},
                "create_ground": True,
                "ground": {"size": 20, "location": [0, 0, 0], "color": [0.2, 0.2, 0.2, 1.0]},
                "objects": [
                    {
                        "type": "CUBE",
                        "size": 2,
                        "location": [0, 0, 1],
                        "rotation": [0, 0, 0],
                        "material": {"name": "Red", "color": [0.8, 0.2, 0.2, 1.0], "metallic": 0.0, "roughness": 0.5},
                    }
                ],
            },
            {
                "name": "blue_sphere",
                "camera": {"location": [0, -8, 3], "rotation": [0.9, 0, 0], "lens": 35},
                "lighting": {"setup": "studio"},
                "objects": [
                    {
                        "type": "SPHERE",
                        "size": 2,
                        "location": [0, 0, 1],
                        "material": {"name": "Blue", "color": [0.2, 0.2, 0.8, 1.0], "metallic": 0.8, "roughness": 0.2},
                    }
                ],
            },
            {
                "name": "multi_objects",
                "camera": {"location": [5, -12, 8], "rotation": [0.8, 0, 0.4]},
                "lighting": {"setup": "outdoor"},
                "objects": [
                    {
                        "type": "CUBE",
                        "size": 1.5,
                        "location": [-2, 0, 0.75],
                        "material": {"name": "Red", "color": [0.8, 0.2, 0.2, 1.0]},
                    },
                    {
                        "type": "SPHERE",
                        "size": 1.5,
                        "location": [0, 2, 0.75],
                        "material": {"name": "Green", "color": [0.2, 0.8, 0.2, 1.0]},
                    },
                    {
                        "type": "CYLINDER",
                        "size": 1.5,
                        "location": [2, 0, 0.75],
                        "material": {"name": "Blue", "color": [0.2, 0.2, 0.8, 1.0]},
                    },
                ],
            },
            {
                "name": "glass_demo",
                "resolution_x": DEFAULT_RESOLUTION_X,
                "resolution_y": DEFAULT_RESOLUTION_Y,
                "samples": DEFAULT_SAMPLES,
                "camera": {"location": [0, -6, 3], "rotation": [0.9, 0, 0]},
                "lighting": {"setup": "studio"},
                "create_ground": True,
                "ground": {"size": 20, "color": [0.3, 0.3, 0.3, 1.0], "roughness": 0.7},
                "objects": [
                    {
                        "type": "SPHERE",
                        "size": 2,
                        "location": [0, 0, 1],
                        "material": {
                            "name": "Glass",
                            "color": [0.9, 0.9, 0.9, 1.0],
                            "metallic": 0.0,
                            "roughness": 0.05,
                            "transmission": 0.95,
                            "ior": 1.45,
                        },
                    }
                ],
            },
        ]
    }

    # Create directory if needed
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # Save the config
    with open(config_path, "w") as f:
        json.dump(sample_config, f, indent=2)

    logger.info(f"Created sample configuration file at: {config_path}")
    return config_path


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch render Blender scenes from a config file")
    parser.add_argument("--config", help="Path to JSON configuration file")
    parser.add_argument(
        "--output",
        help="Directory to save renders",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "batch"),
    )
    parser.add_argument("--create-sample-config", action="store_true", help="Create a sample configuration file")

    args = parser.parse_args()

    # If creating sample config
    if args.create_sample_config:
        if not args.config:
            # Set default config path
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "sample_batch_config.json"
            )
        else:
            config_path = args.config

        create_sample_config(config_path)
        logger.info("Sample configuration created. Run the script with this config to render:")
        logger.info(f"python {sys.argv[0]} --config {config_path} --output {args.output}")
        return

    # If no config file provided
    if not args.config:
        parser.print_help()
        logger.error("\nNo configuration file provided.")
        logger.info("To create a sample configuration, run:")
        logger.info(f"python {sys.argv[0]} --create-sample-config")
        return

    # Render scenes
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output, timestamp)

    logger.info(f"Starting batch render of scenes from: {args.config}")
    logger.info(f"Output will be saved to: {output_dir}")

    rendered_files = render_scenes_from_config(args.config, output_dir)

    logger.info(f"Batch rendering complete. Rendered {len(rendered_files)} scenes:")
    for file_path in rendered_files:
        logger.info(f"  - {file_path}")


if __name__ == "__main__":
    main()
