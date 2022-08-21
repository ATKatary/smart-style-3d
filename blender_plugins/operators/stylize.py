import os
import bpy
import json
import bmesh
import requests 

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

class Stylize_OT_Op(Operator):
    """
    AF() = Uploads a mesh to the backend to be stylized and sent back
    """
    bl_idname = "object.stylize_mesh"
    bl_label = "Stylizes mesh"
    bl_description = "Sends a mesh to backend to be stylized"

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
        obj = context.view_layer.objects.active
        mesh = obj.data
        mesh_data = ""
        selected_vertices = []

        for vertex in  mesh.vertices:
            mesh_data += "v %.4f %.4f %.4f\n" % vertex.co[:]

        for face in mesh.polygons:
            mesh_data += "f"
            for vertex in face.vertices:
                if vertex.select == True: selected_vertices.append(vertex.index)
                mesh_data += f" {vertex + 1}"  
            mesh_data += "\n"
        
        print('Selected:', len(selected_vertices))

        url = "http://0.0.0.0:8000/api/imad/upload"
        params = {'mesh': mesh_data, 'status': "no-save", 'text2mesh': "", "selected": selected_vertices}

        response = requests.get(url=url, params=params).json()
        print(response)
        return {'FINISHED'}
    
    def __str__(self):
        """ Override obj.__str__ """
        return f"Mesh Stylizer"