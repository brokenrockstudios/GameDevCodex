
bl_info = {
    "name": "FBX Bulk Import (.fbx)",
    "author": "Wally & Broken Rock Studios",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "File > Import > FBX Bulk Import (.fbx)",
    "description": "Import every FBX in a folder (optionally recursive), arranged on an evenly-spaced grid so nothing overlaps",
    "category": "Import-Export",
}

import bpy
import os
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty
from bpy_extras.io_utils import ImportHelper


def find_fbx_files(folder, recursive=False):
    fbx_files = []
    if recursive:
        for root, _dirs, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(".fbx"):
                    fbx_files.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder):
            if f.lower().endswith(".fbx"):
                fbx_files.append(os.path.join(folder, f))
    return sorted(fbx_files)


def get_or_create_collection(name, parent_collection):
    """Get a child collection of parent_collection with the given name,
    creating (and linking) it if it doesn't already exist."""
    existing = parent_collection.children.get(name)
    if existing is not None:
        return existing
    new_collection = bpy.data.collections.new(name)
    parent_collection.children.link(new_collection)
    return new_collection


def get_target_collection(root_folder, filepath, root_collection):
    """Given the root import folder and a file's full path, walk/create
    the chain of nested collections matching the subfolder structure and
    return the deepest one (where the file itself lives)."""
    rel_path = os.path.relpath(os.path.dirname(filepath), root_folder)
    collection = root_collection
    if rel_path and rel_path != ".":
        for part in rel_path.split(os.sep):
            collection = get_or_create_collection(part, collection)
    return collection


class IMPORT_OT_batch_fbx_folder(bpy.types.Operator, ImportHelper):
    """Import every FBX file in a folder, spaced out on a grid"""
    bl_idname = "import_scene.batch_fbx_folder"
    bl_label = "Import Folder"
    bl_options = {'REGISTER', 'UNDO'}

    # ImportHelper needs filename_ext, but we're really just using the
    # file browser to pick a directory (directory property below).
    filename_ext = ""

    directory: StringProperty(
        name="Folder Path",
        description="Folder containing FBX files",
        subtype='DIR_PATH',
    )

    # These two together put the file browser into "pick a folder" mode:
    # filter_folder keeps folders selectable/navigable, and leaving
    # filter_glob empty means it won't try to restrict/require a specific
    # file (like an .fbx) to be highlighted before you can confirm.
    filter_folder: BoolProperty(default=True, options={'HIDDEN'})
    filter_glob: StringProperty(default="", options={'HIDDEN'})

    recursive: BoolProperty(
        name="Include Subfolders",
        description="Also search subfolders for FBX files",
        default=True,
    )

    spacing: FloatProperty(
        name="Spacing",
        description="Distance between imported items",
        default=5.0,
        min=0.0,
    )

    columns: IntProperty(
        name="Grid Columns",
        description="Number of items per row before wrapping",
        default=10,
        min=1,
    )

    parent_to_empty: BoolProperty(
        name="Group Under Empty",
        description="Parent each imported FBX's objects to an anchor empty",
        default=False,
    )

    match_folder_structure: BoolProperty(
        name="Match Folder Structure",
        description="Recreate the chosen folder's subfolder structure as nested "
                     "collections, and place each FBX's objects into the collection "
                     "matching where it was found on disk",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "recursive")
        layout.prop(self, "match_folder_structure")
        layout.separator()
        layout.prop(self, "spacing")
        layout.prop(self, "columns")
        layout.prop(self, "parent_to_empty")

    def execute(self, context):
        folder = self.directory

        if not folder or not os.path.isdir(folder):
            self.report({'ERROR'}, "Please choose a valid folder")
            return {'CANCELLED'}

        fbx_files = find_fbx_files(folder, self.recursive)

        if not fbx_files:
            self.report({'WARNING'}, f"No .fbx files found in: {folder}")
            return {'CANCELLED'}

        imported_count = 0

        # Root collection for this whole import, named after the chosen folder,
        # linked into the scene's master collection.
        root_folder_name = os.path.basename(os.path.normpath(folder)) or folder
        if self.match_folder_structure:
            root_collection = get_or_create_collection(root_folder_name, context.scene.collection)
        else:
            root_collection = context.collection

        for index, filepath in enumerate(fbx_files):
            filename = os.path.splitext(os.path.basename(filepath))[0]

            col = index % self.columns
            row = index // self.columns
            x = col * self.spacing
            y = -row * self.spacing
            z = 0.0

            if self.match_folder_structure:
                target_collection = get_target_collection(folder, filepath, root_collection)
            else:
                target_collection = root_collection

            pre_import_objs = set(bpy.data.objects)

            try:
                bpy.ops.import_scene.fbx(filepath=filepath)
            except RuntimeError as e:
                self.report({'WARNING'}, f"Failed to import {filename}: {e}")
                continue

            new_objs = [obj for obj in bpy.data.objects if obj not in pre_import_objs]

            if not new_objs:
                self.report({'WARNING'}, f"No objects imported from {filename}")
                continue

            # Move newly imported objects into the target collection (the FBX
            # importer links them wherever the active collection was).
            for obj in new_objs:
                for coll in list(obj.users_collection):
                    coll.objects.unlink(obj)
                target_collection.objects.link(obj)

            if self.parent_to_empty:
                empty = bpy.data.objects.new(f"{filename}_ANCHOR", None)
                empty.empty_display_size = 0.5
                empty.location = (x, y, z)
                target_collection.objects.link(empty)

                for obj in new_objs:
                    if obj.parent is None or obj.parent not in new_objs:
                        obj.parent = empty
                        obj.matrix_parent_inverse = empty.matrix_world.inverted()
            else:
                roots = [obj for obj in new_objs if obj.parent is None or obj.parent not in new_objs]
                for obj in roots:
                    obj.location.x += x
                    obj.location.y += y
                    obj.location.z += z

            imported_count += 1

        self.report({'INFO'}, f"Imported {imported_count} of {len(fbx_files)} FBX files")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open Blender's file browser in directory-select mode
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_func_import(self, context):
    self.layout.operator(IMPORT_OT_batch_fbx_folder.bl_idname, text="FBX Bulk Import (.fbx)")


def register():
    bpy.utils.register_class(IMPORT_OT_batch_fbx_folder)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(IMPORT_OT_batch_fbx_folder)


if __name__ == "__main__":
    register()
