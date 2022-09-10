"""
imad models
"""
import os
import uuid
import clip
import shlex
import pymeshlab
import subprocess
import numpy as np
from pathlib import Path
import scipy.sparse.linalg
from django.db import models
from scipy.cluster.vq import kmeans2
from .imad_utils.face_graph import FaceGraph
from .text2mesh.implementation.utils import check_mesh
from .text2mesh.text2mesh.main import run_branched
from .text2mesh.text2mesh.args import args
from .x2mesh.implementation.utils import device

### Global Constants ###
alphabet_size = 26
clip_model, preprocess = clip.load('ViT-B/32', device, jit=False)
extract_line_info = lambda line: list(map(lambda x: float(x), line.split(" ")[1:4]))

class Mesh(models.Model):
  """
  AF(id, path) = an mesh created stored at path

  Representation Invariant
    - inherits from models.Model
  
  Representation Exposure
    - inherits from models.Model
    - access allowed to all fields but they are all immutable
  """
  ##### Representation #####
  id_value = uuid.uuid4()
  dir = f"{Path(__file__).parent.absolute()}/models"
  class_dir = f"{Path(__file__).parent.absolute()}/classification"

  stylized = models.BooleanField(default=False)
  faces = models.IntegerField(default=0)
  vertices = models.IntegerField(default=0)
  vertex_normals = models.IntegerField(default=0)
  name = models.CharField(max_length=alphabet_size, default="Vase")
  path = models.CharField(max_length=alphabet_size ** 2, default=f"{dir}/{id_value}.obj")
  id = models.UUIDField(primary_key = True,  editable = False, unique = True, default = id_value)

  def extract(self):
    """
    Extracts the information of the saved mesh and reports it
    """
    with open(self.path, 'r') as script:
      mesh = script.read()
      v, vn, f = 0, 0, 0

      for line in mesh.split("\n"):
        if line.startswith('v '): 
          v += 1 
          # vertices += extract_line_info(line)
        elif line.startswith('vn '): vn += 1
        elif line.startswith('f '): f += 1  

      self.faces = f
      self.vertices = v
      self.vertex_normals = vn
      script.close()

  def overwrite(self, new_mesh):
    """
    Overwirtes the existing model mesh file with another

    Inputs
      :new_mesh: <str> info of new mesh
    """
    with open(self.path, 'w') as script:
      script.seek(0)
      script.truncate(0)
      script.write(new_mesh)
      script.close()

  def text2mesh(self, prompt, selected_verticies, selected_mesh, scaling_factor):
    """
    Stylizes a mesh and stores the stylized output in a stylized file corresponding to self.id file

    Inputs
      :prompt: <str> the string to use for stylizing the mesh
    """
    print("Text2mesh Stylizing ...")
    n_iter = 401
    output_dir = f"{self.dir}/{selected_mesh}"
    try: os.mkdir(output_dir)
    except: pass

    args['n_iter'] = n_iter
    args['prompt'] = prompt
    args['obj_path'] = f"{self.dir}/{selected_mesh}.obj"
    args['output_dir'] = output_dir
    args['verticies_in_file'] = False
    args['selected_vertices'] = selected_verticies
    args['scaling_factor'] = scaling_factor

    check_mesh(f"{self.dir}/{selected_mesh}.obj")
    run_branched(args)

    with open(f"{output_dir}/{selected_mesh}_final_style_0/{selected_mesh}_final{(n_iter // 100) * 100}.obj", 'r') as mesh: 
      return mesh.read()

  def segment(self, k = 12):
    """
    Segments a mesh as follows:
        1. Converts mesh into a face graph, where 
            - each node is a face 
            - faces have edges between them iff they are adjacent 
            - weights of the edge between fi and fj = w(fi, fj) = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist
                - ang_dist(fi, fj) = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180
                - geodisc(fi, fj) = distance from center of fi to center of fj
        2. We compute similarity matrix M
            (How Katz and Tal did it) 
            Decide on k faces (f1, f2, ..., fk) to be the 'centroid nodes' of the graph
            For each node we compute the probability that it belongs to class k 
                - P_j(fi) = [1/w(fi, fj)] / [1/w(fi, f1) + 1/w(fi, f2) + ... + 1/w(fi, fk)]

            (How Liu and Zhang did it) 
            For each pair of nodes (fi, fj) we compute the similarity as 
                - Sim(fi, fj) = e^(-w(fi, fj) / [2 * (avg_w) ** 2]) if w(fi, fj) != inf & fi != fj
                              = 0 if w(fi, fj) == inf
                              = 1 if fi == fj
        3. Compute normal Laplacian of M, L
            - L = sqrt(D).T * M.T * sqrt(D); D is degree matrix of the face graph
        4. We compute eigenvalues and vectors of L
        5. We preform K-means clustering (or other technique) on first k egienvectors

    Inputs
        :mesh: <pymeshlab.Mesh> a mesh specifying the vertices and the faces
        :k: <int | None> clusters to seperate mesh into, if None then number is determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Labels of size m x 1; m = len(mesh.vertex_matrix) where Labels[i] = label of vertex i ∈ [1, k]
    """
    # Step 0
    mesh_set = pymeshlab.MeshSet()
    mesh_set.load_new_mesh(self.path)
    mesh = mesh_set.current_mesh()

    # Step 1
    mesh_graph = FaceGraph(mesh)

    # Step 2
    # if(os.path.exists(f"{model_loc}/similarity_matrix.npy")):
    #     similarity_matrix = np.load(f"{model_loc}/similarity_matrix.npy")
    # else:
    similarity_matrix = mesh_graph.similarity_matrix()

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.degree_matrix)
    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree

    # Step 4
    eigen_values, eigen_vectors = scipy.sparse.linalg.eigsh(laplacian) # Eigen values here can be used to get the value of k  = num < epsilon (0.5)
    eigen_vectors /= np.linalg.norm(eigen_vectors, axis=1)[:,None]

    # Step 5
    _, labels = kmeans2(eigen_vectors, k, minit="++", iter=50)
    vectors_labels = {}
    vectors_labels['vectors'] = eigen_vectors
    vectors_labels['values'] = eigen_values
    vectors_labels['labels']  = labels
    # np.savez(f"{model_loc}/vectors_labels.npz",vectors_labels )
    # print(f"Written labels and vectors to:{model_loc}/vectors_labels.npz")
    return labels

  def remove(self):
    """ Removes the mesh """
    os.remove(self.path)
    os.system(f"rm -rf {self.path}/{self.id}_result")

  def __str__(self) -> str:
    """ Override models.Model.__str__() """
    if self.stylized: return f"Stylized {self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
    return f"{self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
