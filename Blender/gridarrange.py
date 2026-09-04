import bpy
import json
from mathutils import Vector
from bpy.props import FloatProperty, IntProperty, StringProperty


class OBJECT_OT_arrange_selected_grid(bpy.types.Operator):
    """Lay selected top-level objects out on a grid."""

    bl_idname = "object.arrange_selected_grid"
    bl_label = "Arrange Selected on Grid"
    bl_options = {'REGISTER', 'UNDO'}

    columns: IntProperty(
        name="Columns",
        description="Items per row before wrapping to the next row",
        default=10,
        min=1,
    )
    spacing: FloatProperty(
        name="Spacing",
        description="Distance between item origins in the grid",
        default=5.0,
        min=0.0,
    )

    # Stored on the operator so Adjust Last Operation (F9 / lower-left) always
    # recalculates from the original anchor instead of accumulating offsets.
    initial_state: StringProperty(options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and bool(context.selected_objects)

    @staticmethod
    def selected_roots(context):
        selected = set(context.selected_objects)
        # A selected child follows its selected parent, so only parents occupy
        # grid cells and a hierarchy stays together.
        return sorted(
            (obj for obj in selected if obj.parent not in selected),
            key=lambda obj: obj.name.casefold(),
        )

    def capture_initial_state(self, context):
        objects = self.selected_roots(context)
        if not objects:
            self.report({'ERROR'}, "Select one or more objects to arrange")
            return False

        locations = [obj.matrix_world.translation for obj in objects]
        self.initial_state = json.dumps({
            # Keep the grid's upper-left corner at the existing selection edge.
            "anchor": (
                min(location.x for location in locations),
                max(location.y for location in locations),
                min(location.z for location in locations),
            ),
            "objects": [obj.name for obj in objects],
        })
        self.columns = min(self.columns, len(objects))
        return True

    def invoke(self, context, event):
        if not self.capture_initial_state(context):
            return {'CANCELLED'}
        return self.execute(context)

    def execute(self, context):
        # Supports UI paths that execute directly rather than invoking first.
        if not self.initial_state and not self.capture_initial_state(context):
            return {'CANCELLED'}

        try:
            state = json.loads(self.initial_state)
            anchor = Vector(state["anchor"])
            objects = [bpy.data.objects.get(name) for name in state["objects"]]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self.report({'ERROR'}, "Grid layout state is invalid; run the operator again")
            return {'CANCELLED'}

        objects = [obj for obj in objects if obj is not None]
        if not objects:
            self.report({'ERROR'}, "None of the stored grid objects still exist")
            return {'CANCELLED'}

        for index, obj in enumerate(objects):
            column = index % self.columns
            row = index // self.columns
            matrix = obj.matrix_world.copy()
            matrix.translation = anchor + Vector((
                column * self.spacing,
                -row * self.spacing,
                0.0,
            ))
            obj.matrix_world = matrix

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "columns")
        layout.prop(self, "spacing")


def menu_func_object(self, context):
    self.layout.separator()
    self.layout.operator(OBJECT_OT_arrange_selected_grid.bl_idname, icon='GRID')


def register():
    bpy.utils.register_class(OBJECT_OT_arrange_selected_grid)
    bpy.types.VIEW3D_MT_object.append(menu_func_object)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func_object)
    bpy.utils.unregister_class(OBJECT_OT_arrange_selected_grid)


if __name__ == "__main__":
    register()
