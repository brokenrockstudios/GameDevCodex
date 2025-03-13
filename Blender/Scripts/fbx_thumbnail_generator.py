# Copyright Broken Rock Studios LLC. All Rights Reserved.
# See the LICENSE file for details.


# FBX Thumbnail Generator using Blender
# If you have a folder full of fbx and want to generate a bunch of png for preview purposes of each one.
# Run this script against the folder and it will generate a barrel.png for a barrel.fbx file

# "c:\Program Files\Blender foundation\Blender 4.2\blender.exe" --background --python .\fbx_thumbnail_generator.py -- .\fbx\filelocation\ 512

import bpy
import os
import sys
import math
import mathutils

# Get arguments after the '--' flag
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

# Parse command line arguments
input_dir = argv[0] if len(argv) > 0 else "."
output_dir = None  # Always save thumbnails next to FBX files
thumbnail_size = int(argv[1]) if len(argv) > 1 else 512  # Default size: 512x512

def setup_scene():
    """Set up a clean scene with good rendering settings"""
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a new camera with good positioning
    bpy.ops.object.camera_add(location=(0, -10, 0), rotation=(math.pi/2, 0, 0))
    camera = bpy.context.object
    camera.name = "ThumbnailCamera"
    
    # Set the camera as the active camera for the scene
    bpy.context.scene.camera = camera
    
    # Set up lighting (simple three-point lighting)
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
    key_light = bpy.context.object
    key_light.name = "KeyLight"
    key_light.data.energy = 500
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -3, 3))
    fill_light = bpy.context.object
    fill_light.name = "FillLight"
    fill_light.data.energy = 250
    
    # Back light
    bpy.ops.object.light_add(type='AREA', location=(0, 6, 4))
    back_light = bpy.context.object
    back_light.name = "BackLight"
    back_light.data.energy = 300
    
    # Set rendering settings
    bpy.context.scene.render.resolution_x = thumbnail_size
    bpy.context.scene.render.resolution_y = thumbnail_size
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.engine = 'CYCLES'  # Or 'BLENDER_EEVEE' for faster but less quality
    
    # If using Cycles, set some optimized settings for thumbnails
    if bpy.context.scene.render.engine == 'CYCLES':
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.preview_samples = 32
    
    # Set background to a neutral gradient
    world = bpy.context.scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark gray

def import_fbx(fbx_path):
    """Import an FBX file"""
    try:
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        
        # Apply default Blender gray material to all objects
        default_material = bpy.data.materials.new(name="DefaultGray")
        default_material.use_nodes = True
        bsdf = default_material.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            # Set to medium gray
            bsdf.inputs['Base Color'].default_value = (0.4, 0.4, 0.4, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.0
            
            # Check if 'Specular' input exists (for Blender 4.0 and older)
            if 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = 0.5
            # For Blender 4.2+ try 'Specular IOR Level' instead
            elif 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = 0.5
                
            bsdf.inputs['Roughness'].default_value = 0.5
        
        # Apply the material to all mesh objects
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Assign default material to all mesh objects
                if len(obj.material_slots) == 0:
                    obj.data.materials.append(default_material)
                else:
                    for i in range(len(obj.material_slots)):
                        obj.material_slots[i].material = default_material
        
        return True
    except Exception as e:
        print(f"Error importing {fbx_path}: {e}")
        return False

def frame_objects():
    """Frame all objects in the camera view without using view3d operators"""
    # Select all meshes
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    
    # If no meshes were found, return False
    if not mesh_objects:
        print("No mesh objects found")
        return False
    
    # Get the bounding box corners of all mesh objects
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    for obj in mesh_objects:
        # Get global bounding box corners
        for corner in obj.bound_box:
            # Convert local coordinates to global
            global_corner = obj.matrix_world @ mathutils.Vector(corner)
            
            min_x = min(min_x, global_corner.x)
            min_y = min(min_y, global_corner.y)
            min_z = min(min_z, global_corner.z)
            max_x = max(max_x, global_corner.x)
            max_y = max(max_y, global_corner.y)
            max_z = max(max_z, global_corner.z)
    
    # Calculate center and dimensions of the bounding box
    center = mathutils.Vector(((max_x + min_x) / 2, (max_y + min_y) / 2, (max_z + min_z) / 2))
    dimensions = mathutils.Vector((max_x - min_x, max_y - min_y, max_z - min_z))
    
    # Get the maximum dimension to ensure everything is in view
    max_dim = max(dimensions)
    
    # Position and orient the camera
    camera = bpy.context.scene.camera
    if not camera:
        print("No active camera")
        return False
    
    # Set camera position based on the bounding box
    # Position the camera at an isometric-like view
    distance = max_dim * 1.5  # Adjust multiplier as needed
    camera.location = center + mathutils.Vector((distance, -distance, distance))
    
    # Point camera to the center of all objects
    direction = center - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Set camera properties for better framing
    if camera.data.type == 'PERSP':
        # For perspective camera, adjust the field of view
        camera.data.lens = 50  # 50mm is a standard lens
    
    return True

def render_thumbnail(output_path):
    """Render the thumbnail and save it"""
    # Set output path
    bpy.context.scene.render.filepath = output_path
    
    # Render image
    bpy.ops.render.render(write_still=True)

def process_fbx_file(fbx_path, output_dir=None):
    """Process a single FBX file and generate a thumbnail"""
    print(f"Processing: {fbx_path}")
    
    # Set up a new clean scene
    setup_scene()
    
    # Import the FBX
    if not import_fbx(fbx_path):
        print(f"Failed to import {fbx_path}. Skipping...")
        return False
    
    # Frame objects in camera view
    if not frame_objects():
        print(f"No mesh objects found in {fbx_path} or camera positioning failed. Skipping...")
        return False
    
    # Get absolute paths
    abs_fbx_path = os.path.abspath(fbx_path)
    output_path = os.path.splitext(abs_fbx_path)[0] + ".png"
    
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Will save thumbnail to: {output_path}")
    
    # Render thumbnail
    render_thumbnail(output_path)
    
    print(f"Thumbnail saved to: {output_path}")
    return True

def batch_process(input_dir):
    """Process all FBX files in the input directory"""
    # Find all FBX files
    fbx_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.fbx'):
                fbx_files.append(os.path.join(root, file))
    
    if not fbx_files:
        print(f"No FBX files found in {input_dir}")
        return
    
    print(f"Found {len(fbx_files)} FBX files to process")
    
    # Process each FBX file
    success_count = 0
    for fbx_path in fbx_files:
        if process_fbx_file(fbx_path):
            success_count += 1
    
    print(f"Processed {success_count} of {len(fbx_files)} FBX files successfully")

# Run the batch process
batch_process(input_dir)
