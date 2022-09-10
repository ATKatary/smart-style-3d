"""
imad views
"""
import os
import json
import pymeshlab
import numpy as np
from tqdm import tqdm
from .models import Mesh
from rest_framework import status
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .imad_utils.view_helpers import _is_subset

### Global Constants ###
save = "save"
report = lambda error: f"----------------------------\n{error}\n----------------------------\n"
colors = [[1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 0.8, 1, 1], [1, 0.1, 0.6, 1], [1, 0.647, 0, 1],
          [0.4, 0.4, 0.4, 1], [0.4, 0, 0, 1], [0, 0.4, 0, 1], [0, 0, 0.4, 1], [0.4, 0.32, 0.4, 1], [0.4, 0.04, 0.24, 1], [0.4, 0.2588, 0, 1]]

@api_view(['GET'])
def fetch(request, *args, **kwargs):
    """
    Fetches model with given id

    Inputs
       :param request: <HttpRequest> containing all relevant information for the event to be fetched
    
    Output
       :returns: Status ... 
                        ... HTTP_200_OK if the model is fetched successfully
                        ... HTTP_404_NOT_FOUND if no such model exists
                        ... HTTP_403_FORIBIDDEN if the model couldn't be fetched
    """
    data = []
    request = request.GET
    fetch_fields = ["modelId"]
    event_status   = _is_subset(fetch_fields, request.keys())
    
    if event_status == status.HTTP_200_OK:
        model_id = request['modelId']
        
        mesh = Mesh.objects.get(id=model_id)
        
        if mesh: data['meshPath'] = mesh.path
        else: event_status = status.HTTP_404_NOT_FOUND
    
    return Response(status = event_status, data = data)

@api_view(['GET'])
def stylize(request, *args, **kwargs):
    """
    Uploads model with given id

    Inputs
       :param request: <HttpRequest> containing all relevant information for the uploading of a mesh
    
    Output
       :returns: Status ... 
                        ... HTTP_200_OK if the model is uploaded successfully
                        ... HTTP_404_NOT_FOUND if no such model uploaded
                        ... HTTP_403_FORIBIDDEN if the model couldn't be uploaded
    """
    data = {}
    request = request.GET
    fetch_fields = ["mesh", "status", "text2mesh", "selected", "selected_mesh"]
    event_status = _is_subset(fetch_fields, request.keys())
    
    if event_status == status.HTTP_200_OK:
        mesh_data = request['mesh']
        prompt = request['text2mesh']
        mesh_status = request['status']
        selected_segments = request['selected']
        selected_mesh = request['selected_mesh']
        scaling_factor = float(request['scaling_factor'])

        mesh = Mesh()
        if selected_mesh != "": mesh.path = f"{mesh.dir}/{selected_mesh}.obj"
        else: mesh.overwrite(mesh_data)
        mesh.extract()

        selected_verticies = ""
        if selected_segments != "": 
            for i in selected_segments.split(" "):
                with open(f"{mesh.dir}/{selected_mesh}/segment_{i}.txt", "r") as segment:
                    selected_verticies += f"{segment.read()}\n"

        try:
            stylized_mesh = mesh.text2mesh(prompt, selected_verticies, selected_mesh, scaling_factor)
            data['stylized_mesh'] = stylized_mesh
        except Exception as error: raise error; print(f"Error occured while stylizing\n{report(error)}")

        if mesh_status == save: mesh.save()
        # mesh.remove()

    return Response(status = event_status, data = data)

@api_view(['GET'])
def segment(request, *args, **kwargs):
    """
    Segments a model using a specified mode, one of (spectural, base)

    Inputs
       :param request: <HttpRequest> containing all relevant information for the segmentation of a mesh (mesh, mode)
                                     mesh is a string representing the mesh in obj
    
    Output
       :returns: Status ... 
                        ... HTTP_200_OK if the model is uploaded successfully
                        ... HTTP_404_NOT_FOUND if no such model uploaded
                        ... HTTP_403_FORIBIDDEN if the model couldn't be uploaded
    """
    data = {}
    request = request.GET
    segment_fields = ["mesh", "mode"]
    segment_status = _is_subset(segment_fields, request.keys())

    if segment_status == status.HTTP_200_OK:
        mode = request['mode']
        mesh_data = request['mesh']
        selected_mesh = request['selected_mesh']

        mesh = Mesh()
        if selected_mesh != "": mesh.path = f"{mesh.dir}/{selected_mesh}.obj"
        else: mesh.overwrite(mesh_data)
        mesh.extract()

        try:
            print(selected_mesh)

            mesh_set = pymeshlab.MeshSet()
            mesh_set.load_new_mesh(mesh.path)
            mesh_labels = mesh.segment() 
            
            faces = mesh_set.current_mesh().face_matrix()
            vertices = mesh_set.current_mesh().vertex_matrix()

            m = faces.shape[0]
            face_colors = np.zeros((m, 4))
            for i in tqdm(range(m)):
                face_colors[i] = colors[mesh_labels[i]]

            mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces, f_color_matrix=face_colors))
            mesh_set.save_current_mesh(f"{mesh.dir}/{selected_mesh}_segmented.obj")

            labels_to_vertices = {i: set() for i in range(len(set(mesh_labels)))}
            for i, face in enumerate(mesh_labels):
                for v in faces[i]:
                    labels_to_vertices[face].add(v)

            try: os.mkdir(f"{mesh.dir}/{selected_mesh}")
            except: pass

            for label, vertices in labels_to_vertices.items():
                with open(f"{mesh.dir}/{selected_mesh}/segment_{label}.txt", "w") as segmented_part:
                    for v in vertices:
                        segmented_part.write(f"{v}\n")
                segmented_part.close()

            data['faces'] = mesh_labels
            try:
                data['labels'] = [class_ for _, class_ in json.loads(open(f"{mesh.class_dir}/{selected_mesh}.json", "r").read()).items()]
            except Exception as error: print(f"Error occured while getting classified labels\n{report(error)}") 

        except Exception as error: print(f"Error occured while segmenting\n{report(error)}")
        
    return Response(status = segment_status, data = data)

