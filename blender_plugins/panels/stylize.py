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
        
        layout.label(text="Mesh")
        mesh_col = layout.column()
        mesh_row = mesh_col.row()
        mesh_row.prop(context.scene, "selected_mesh")
        mesh_col.operator("object.insert_mesh", icon = "ADD")

        layout.separator()

        layout.label(text="Prompt")
        prompt_col = layout.column()

        prompt_row = prompt_col.row()
        prompt_row.prop(context.scene, "prompt")

        layout.separator()

        layout.label(text="Base Segment")
        base_segment_row = layout.row()
        base_segment_col = base_segment_row.column()
        base_segment_col.operator("object.base_segment_mesh", icon = "PLUGIN")
 
        layout.separator()

        layout.label(text="Spectural Segment")
        segment_row = layout.row()
        segment_col = segment_row.column()
        segment_col.operator("mesh.segment_mesh", icon = "PLUGIN")

        layout.separator()

        stylize_row = layout.row()
        stylize_col = stylize_row.column()
        stylize_col.operator("object.stylize_mesh", icon = "PLUGIN")




