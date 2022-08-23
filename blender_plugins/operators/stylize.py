import os
import bpy
import json
import bmesh
import requests 
from bpy.types import Operator
from bpy.props import EnumProperty


### Global COnstants ###
meshes = {"0": "vase", "1": "pencil_holder", "2": "lamp"}
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Stylize_OT_Op(Operator):
    """
    AF() = Uploads a mesh to the backend to be stylized and sent back
    """
    bl_idname = "object.stylize_mesh"
    bl_label = "Stylizes mesh"
    bl_description = "Sends selected mesh to backend to be stylized"

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
        prompt = context.scene.prompt
        obj = context.view_layer.objects.active
        
        mesh_data = ""
        selected_vertices = ""
        mesh = bmesh.from_edit_mesh(obj.data)
        selected_mesh = context.scene.selected_mesh
        selected_mesh = meshes[selected_mesh]
    
        for vertex in mesh.verts:
            if vertex.select == True: selected_vertices += f"{vertex.index}\n"
            mesh_data += "v %.4f %.4f %.4f\n" % vertex.co[:]
            mesh_data += "vn %.4f %.4f %.4f\n" % vertex.normal[:]

        for face in obj.data.polygons:
            mesh_data += "f"
            for vertex in face.vertices:
                mesh_data += f" {vertex + 1}"  
            mesh_data += "\n"
        
        print(f"Prompt:\t{prompt}")
        print(f"Object:\t{context.scene.selected_mesh}")
        print(f"Selected:\t{len(selected_vertices)} vertices")

        url = "http://0.0.0.0:8001/api/imad/upload"
        params = {'mesh': "mesh_data", 'status': "no-save", 'text2mesh': prompt, 'selected': selected_vertices, 'selected_mesh': selected_mesh}

        try:
            response = requests.get(url=url, params=params).json()

            stylized_mesh = response['stylized_mesh']
            with open("./stylized_mesh.obj", "w") as script:
                script.write(stylized_mesh)
        
            bpy.ops.import_scene.obj(filepath="./stylized_mesh.obj")

        except Exception as error: print(f"Error occured while stylizing mesh\n{report(error)}")
        
        return {'FINISHED'}

    def __str__(self):
        """ Override obj.__str__ """
        return f"Mesh Stylizer"