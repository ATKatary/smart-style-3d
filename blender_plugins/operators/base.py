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

class Base_OT_Op(Operator):
    """
    AF() = Finds the base of a mesh
    """
    bl_idname = "object.base_segment_mesh"
    bl_label = "Segment base(s)"
    bl_description = "Segments mesh and tries to find base for now"

    @classmethod
    def poll(cls, context):
        """ Indicates weather the operator should be enabled """
        obj = context.object
        if obj is not None and obj.mode == "EDIT":
            return True
        print("Not in Edit mode")
        return False

    def execute(self, context):
        """ Executes the operator and stores the selected vertices in the selected directory """
        selected_mesh = context.scene.selected_mesh
        print(f"Selected Mesh:\t{selected_mesh}")

        
        obj = context.view_layer.objects.active
        mesh = bmesh.from_edit_mesh(obj.data)
        extremas = _get_extremas(mesh)

        x_extremas = extremas['x']
        y_extremas = extremas['y']
        z_extremas = extremas['z']

        try: 
            print(f">> max_x: {len(x_extremas[0])} v => {mesh.verts[x_extremas[0][0]].co[0]}")
            print(f">> min_x: {len(x_extremas[1])} v => {mesh.verts[x_extremas[1][0]].co[0]}\n")
            
            print(f">> max_y: {len(y_extremas[0])} v => {mesh.verts[y_extremas[0][0]].co[1]}")
            print(f">> min_y: {len(y_extremas[1])} v => {mesh.verts[y_extremas[1][0]].co[1]}\n")

            print(f">> max_z: {len(z_extremas[0])} v => {mesh.verts[z_extremas[0][0]].co[2]}")
            print(f">> min_z: {len(z_extremas[1])} v => {mesh.verts[z_extremas[1][0]].co[2]}\n")
        except: pass

        for i in y_extremas[0]:
            mesh.verts[i].select = True

        with open("min_y_vertices.txt", "w") as vertices_not_to_change:
            for j in y_extremas[1]:
                mesh.verts[j].select = True
                vertices_not_to_change.write(f"{j}\n")

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}

    def __str__(self):
        """ Override obj.__str__ """
        return f"Mesh Inserter"

def _get_extremas(mesh):
    """
    """
    extremes = _get_extremes(mesh)

    min_x, max_x = extremes[0]
    min_y, max_y = extremes[1]
    min_z, max_z = extremes[2]

    e = 0.0
    extremas = {"x": [[], []], "y": [[], []], "z": [[], []]}
    for i in range(len(mesh.verts)):
        vertex = mesh.verts[i].co
        x, y, z = vertex
        x, y, z = float(x), float(y), float(z)
  
        if max_x - e <= x <= max_x: extremas["x"][0].append(i)
        if max_y - e <= y <= max_y: extremas["y"][0].append(i)
        if max_z - e <= x <= max_z: extremas["z"][0].append(i)
        
        if min_x <= x <= min_x + e: extremas["x"][1].append(i)
        if min_y <= y <= min_y + e: extremas["y"][1].append(i)
        if min_z <= z <= min_z + e: extremas["z"][1].append(i)
    return extremas

def _get_extremes(mesh):
    max_x = None
    max_y = None
    max_z = None

    min_x = None
    min_y = None
    min_z = None

    for vert in mesh.verts:
        x, y, z = vert.co
        max_x = _update_max(x, max_x)
        max_y = _update_max(y, max_y)
        max_z = _update_max(z, max_z)

        min_x = _update_min(x, min_x)
        min_y = _update_min(y, min_y)
        min_z = _update_min(z, min_z)
    return (max_x, min_x), (max_y, min_y), (max_z, min_z)

def _update_max(max_v, v):
    if v is None: return max_v
    if v < max_v: return max_v
    return v

def _update_min(max_v, v):
    if v is None: return max_v
    if v > max_v: return max_v
    return v