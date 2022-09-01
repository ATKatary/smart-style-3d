import os
import torch
import pymeshlab
import numpy as np
import kaolin as kal
from utils import device
from kaolin.io.obj import (import_mesh)
from torch.nn.functional import (normalize)

class Mesh():
    """
    AF(path, color) = a mesh representation of a 3d mesh object stored in path, initially set to color

    Representation Invariant:
        - true

    Representation Exporsure:
        - all fields are public for access
    """
    def __init__(self, path, color = torch.tensor([0.0, 0.0, 1.0])):
        self.path = path
        self.obj = import_mesh(path, with_normals=True)

        self.faces = self.obj.faces.to(device)
        self.vertices = self.obj.vertices.to(device)
        self.face_normals = normalize(self.obj.face_normals.to(device).float())
        self.vertex_normals = normalize(self.obj.vertex_normals.to(device).float())
        self.base_color = torch.full(size=(self.faces.shape[0], 3, 3), fill_value=0.5, device=device)
        
        self.color = None
        self.face_uvs = None
        self.texture_map = None
        self.face_attributes = None

        self.set_texture_map_from_color(color)
        self.set_face_attributes_from_color(None)
    
    ### Helper Methods ###
    def set_texture_map_from_color(self, color):
        """
        Generates a texture map given a specific color of size (batch_size, colors = 3, h = 224, w = 224) 

        Inputs
            :color: <tensor> of color to generate texture map, has size (3 for rgb)
        """
        h, w = 224, 224
        texture_map = torch.zeros(1, h, w, 3).to(device)
        texture_map[:, :, :] = color
        self.texture_map = texture_map.permute(0, 3, 1, 2)

    def set_face_attributes_from_color(self, color):
        """
        Generatesface features given a specific color of size (batch_size, n_faces, face_vertices = 3, colors = 3)

        Inputs
            :color: <tensor> of color to generate face features, has size (3 for rgb)
        """
        if color is None: self.face_attributes = self.base_color
        else: self.face_attributes = self.base_color + kal.ops.mesh.index_vertices_by_faces(color.unsqueeze(0), self.faces)
        self.color = color
        
    def export(self, path, color = False):
        """
        Exports the mesh to a file with a given color

        Inputs
            :path: <str> path to the file to export the mesh to
            :color: <boolean> indicating whether to save mesh color or not 
        """
        faces =  np.float64(self.faces.cpu().numpy())
        vertices = np.float64(self.vertices.cpu().numpy())
        vertex_normals = np.float64(self.vertex_normals.cpu().numpy())
        
        if color:
            colors = np.zeros((vertices.shape[0], 4))
            for i, [r, g, b] in enumerate(np.float64(self.color.cpu().numpy())):
                colors[i] = np.array([r, g, b, 1])

        name, ext = os.path.splitext(os.path.basename(self.path))
        mesh_set = pymeshlab.MeshSet()
        mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces, v_normals_matrix=vertex_normals, v_color_matrix=colors))
        mesh_set.save_current_mesh(path)

        # with open(path, "w+") as mesh_file:
        #     for i, vertex in enumerate(self.vertices):
        #         x, y, z = vertex
        #         mesh_file.write(f"v {x} {y} {z}")
        #         if color is not None: 
        #             r, g, b = color[i]
        #             mesh_file.write(f" {r} {g} {b}")
        #         mesh_file.write("\n")
            
        #         if self.vertex_normals is not None:
        #             x, y, x = self.vertex_normals[i]
        #             mesh_file.write(f"vn {x} {y} {z}\n")
        #     mesh_file.write("########## faces ##########\n")
        #     for face in self.faces:
        #         v1, v2, v3 = face
        #         mesh_file.write(f"v {v1} {v2} {v3}\n")
            
        #     mesh_file.write(f"########## {name} ##########\n")
        #     mesh_file.write(f"##### faces: {len(self.faces)}\n")
        #     mesh_file.write(f"##### vertices: {len(self.vertices)}\n")
        #     mesh_file.write(f"##### vertex normals: {len(self.vertex_normals)}\n\n")
        #     mesh_file.write("########## vertices ##########\n")
        #     mesh_file.close()
