import os
import bpy
import json
import bmesh
import requests 
from pathlib import Path
from bpy.types import Operator
from bpy.props import EnumProperty

### Global Constants ###
meshes = {"0": "vase.obj", "1": "pencil_holder.obj", "2": "lamp.obj"}
models_dir = f"{Path(__file__).parent.absolute()}/models"

class Insert_OT_Op(Operator):
    """
    AF() = Uploads a mesh to the backend to be stylized and sent back
    """
    bl_idname = "object.insert_mesh"
    bl_label = "Inserts mesh"
    bl_description = "Adds the selected mesh to the scene"

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        selected_mesh = context.scene.selected_mesh
        if selected_mesh is not None:
            return True
        print("No mesh selected")
        return False

    def execute(self, context):
        """ Executes the operator and stores the selected vertices in the selected directory """
        selected_mesh = context.scene.selected_mesh
        print(f"Selected Mesh:\t{selected_mesh}")

        mesh_path = meshes[selected_mesh]
        bpy.ops.import_scene.obj(filepath=f"{models_dir}/{mesh_path}")

        return {'FINISHED'}

    def __str__(self):
        """ Override obj.__str__ """
        return f"Mesh Inserter"