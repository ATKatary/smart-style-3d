import bpy

from bpy.types import Panel

class Selector_PT_Panel(Panel):
    """
    AF() = a panel for SmartStyle3D vertex selection
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Vertex selector"
    bl_category = "SmartStyle3D"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        layout.prop(context.scene, "directory")
        op = layout.operator("object.get_selected_vertices")
        print(f"Selected storage directory: {context.scene.directory}")
        if hasattr(op, "directory"): op.directory = context.scene.directory
        else: print("Operator does not have directory attribute")

        row = layout.row()
        col = row.column()

        col.operator("object.get_selected_vertices")
