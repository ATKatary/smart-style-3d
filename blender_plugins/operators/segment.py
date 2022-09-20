
import bpy
import json
import bmesh
import requests 
from .utils.actions import assign_materials

### Global Constants ###
meshes = {"0": "vase", "1": "pencil_holder", "2": "lamp", "3": "can_holder", "4": "phone_holder", "5": "phone_holder_decimated", "6": "wrist_thing", "7": "ring"}
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"

class Segment_OT_Op(bpy.types.Operator):
    """ Segment a mesh """

    bl_idname = "mesh.segment_mesh"
    bl_label = "Segment mesh"
    
    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None:
            return True
        print("Failed to get model because no object is selected")
        return False

    def execute(self, context):
        """Executes the segmentation"""
        if bpy.ops.mesh.separate(type='LOOSE') != {'CANCELLED'}:
            self.report({'ERROR'}, "Separated not connected parts, choose "
                                   "one of them for segmentation!")
            return {'CANCELLED'}
        else:
            obj = context.view_layer.objects.active
            selected_mesh = context.scene.selected_mesh
            selected_mesh = meshes[selected_mesh]
            
            # mesh_data = ""
            # for vertex in obj.data.vertices:
            #     mesh_data += "v %.4f %.4f %.4f\n" % vertex.co[:]
            #     mesh_data += "vn %.4f %.4f %.4f\n" % vertex.normal[:]

            # for face in obj.data.polygons:
            #     mesh_data += "f"
            #     for vertex in face.vertices:
            #         mesh_data += f" {vertex + 1}"  
            #     mesh_data += "\n"

            url = "http://0.0.0.0:8000/api/imad/segment"
            
            data = {'mesh': "mesh_data", 'selected_mesh': selected_mesh, 'mode': "spectural"}

            try:
                response = requests.get(url=url, params=data).json()
                # faces = response['faces']
                labels = ["function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function"]

                # labels = response['labels']
                with open("./speedup.json") as labels_file:
                    faces = json.loads(labels_file.read())
                # k = response['k']
                k = 12
                # print(f"[labels] >> {labels}")


                self.report({'INFO'}, f"Segmented mesh into {k} parts successfully!")
                print(f"[context] >> {context}")
                assign_materials(obj, k, faces, context, labels)

            except Exception as error: raise error; print(f"Error occured while segmenting mesh\n{report(error)}")
            
            return {'FINISHED'}