import os
import bpy
import json
import bmesh
import requests 
from pathlib import Path
from bpy.types import Operator
from bpy.props import EnumProperty


### Global COnstants ###
# meshes = {"0": "vase", "1": "pencil_holder", "2": "lamp", "3": "can_holder", "4": "phone_holder", "5": "phone_holder_decimated", "6": "wrist_thing", "7": "ring"}
meshes = {"0": "vase", "1":'battery_dispenser', '2':'bulbasaur', '3':'cutlery_dispenser','4':'headphone_stand', '5':'occarina',"6": "wrist_thing", "7":"Airpods_cover.obj"}
scaling_factors = {"0": "0.4", "1": "5", "2": "1", "3": "5", "4": "50", "5": "10", "6": "1", "7": "1"}
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Stylize_OT_Op(Operator):
    """
    AF() = Uploads a mesh to the backend to be stylized and sent back
    """
    bl_idname = "object.stylize_mesh"
    bl_label = "Stylize mesh"
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
        selected_segments = []
        mesh = bmesh.from_edit_mesh(obj.data)
        i = context.scene.selected_mesh
        selected_mesh = meshes[i]
        selected_vertices = ""
        for segment in context.scene.segments:
            if not segment.selected: continue
            selected_segments.append(segment.i)
        selected_segments = " ".join(str(i) for i in selected_segments)
        for vertex in mesh.verts:
            if vertex.select == True: selected_vertices += f"{vertex.index}\n"
            mesh_data += "v %.4f %.4f %.4f\n" % vertex.co[:]
            mesh_data += "vn %.4f %.4f %.4f\n" % vertex.normal[:]

        for face in obj.data.polygons:
            mesh_data += "f"
            for vertex in face.vertices:
                mesh_data += f" {vertex + 1}"  
            mesh_data += "\n"

        with open("./vertices_headphone_stand_final.txt", 'w') as fi:
            fi.write(selected_vertices)

        
        print(f"Prompt:\t{prompt}")
        print(f"Object:\t{context.scene.selected_mesh}")
        print(f"Selected:\t{len(selected_segments)} segments")
        with open("./original_mesh_headphone_stand.obj", "w") as script:
                script.write(mesh_data)

        with open(f"{Path(__file__).parent.absolute()}/selected_segments.txt", "w") as verts:
            verts.write(selected_segments)

        url = "http://0.0.0.0:8000/api/imad/stylize"

        headers = {"Content-Type": "application/json; charset=utf-8"}

        
        if selected_mesh is not None: mesh_data = ""
        data = {'mesh': mesh_data, 'status': "no-save", 'text2mesh': prompt, 'selected': selected_segments, 'selected_vertices':selected_vertices, 'selected_mesh': selected_mesh, 'scaling_factor': scaling_factors[i]}

        try:
            response = requests.get(url=url, params = data).json()

            stylized_mesh = response['stylized_mesh']
            with open("./stylized_mesh.obj", "w") as script:
                script.write(stylized_mesh)

            bpy.ops.import_scene.obj(filepath="./stylized_mesh.obj")

        except Exception as error: print(f"Error occured while stylizing mesh\n{report(error)}")
        
        return {'FINISHED'}

    def __str__(self):
        """ Override obj.__str__ """
        return f"Mesh Stylizer"
