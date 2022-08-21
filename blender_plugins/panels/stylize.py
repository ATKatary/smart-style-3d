import bpy

from bpy.types import Panel

class SmartStyle3D_PT_Panel(Panel):
    """
    AF() = a panel for SmartStyle3D
    """
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
    bl_label = "Smart Style 3D"
    bl_category = "SmartStyle3D"

    def draw(self, context):
        """ Draws out the ui panel """
        layout = self.layout
        layout.prop(context.scene, "directory")
       
        row = layout.row()
        col = row.column()
        col.operator("object.stylize_mesh")
