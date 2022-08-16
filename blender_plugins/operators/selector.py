import os
import bpy
import bmesh

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

class Selector_OT_Op(Operator):
    """
    AF(directory) = stores the selected vertices in speficied directory
    """
    bl_idname = "object.get_selected_vertices"
    bl_label = "Get selected vertices"
    bl_description = "Creates a file containing all selected vertices"
    filter_folder = BoolProperty(default=True)
    directory: StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None and obj.mode == "EDIT":
            return True
        print("Failed to get selected vertices because object is not in edit mode")
        return False

    def execute(self, context):
        """ Executes the operator and stores the selected vertices in the selected directory """
        selected_vertices = []
        obj = context.view_layer.objects.active
        mesh = bmesh.from_edit_mesh(obj.data)
        storage_path = os.path.join(self.directory, f"{obj.name}.txt")

        print(f"Storing selected vertices in {storage_path}...")
        with open(storage_path, "w") as file:
            for vertex in mesh.verts:
                if vertex.select == True:
                    selected_vertices.append(vertex.index)
                    file.write(f"{vertex.index}\n")

        print('Selected:', len(selected_vertices))
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def __str__(self):
        """ Override obj.__str__ """
        return f"Selected vertices stored at: {self.directory}"
