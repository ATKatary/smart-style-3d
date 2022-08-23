"""
imad models
"""
import os
import uuid
import clip
import shlex
import subprocess
from .args import args
from pathlib import Path
from django.db import models
from .x2mesh.implementation.main import x2mesh
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

  stylized = models.BooleanField(default=False)
  faces = models.IntegerField(default=0)
  vertices = models.IntegerField(default=0)
  vertex_normals = models.IntegerField(default=0)
  name = models.CharField(max_length=alphabet_size, default="Vase")
  path = models.CharField(max_length=alphabet_size ** 2, default=f"{dir}{id_value}.obj")
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

  def text2mesh(self, prompt, vertices_to_not_change, selected_mesh):
    """
    Stylizes a mesh and stores the stylized output in a stylized file corresponding to self.id file

    Inputs
      :prompt: <str> the string to use for stylizing the mesh
    """
    print("Text2mesh Stylizing ...")
    n_iter = 401
    output_dir = f"{self.dir}/{self.id}_result"
    os.mkdir(output_dir)

    args['n_iter'] = n_iter
    args['prompt'] = prompt
    args['output_dir'] = output_dir
    args['verticies_in_file'] = False
    args['obj_path'] = f"{self.dir}/{selected_mesh}.obj"
    args['vertices_to_not_change'] = vertices_to_not_change
    
    x2mesh(args, clip_model, preprocess)

    with open(f"{output_dir}/{selected_mesh}_final_style_0/vase_{(n_iter // 100) * 100}_iters.obj", 'r') as mesh: 
      return mesh.read()

  def remove(self):
    """ Removes the mesh """
    os.remove(self.path)
    os.system(f"rm -rf {self.dir}/{self.id}_result")

  def __str__(self) -> str:
    """ Override models.Model.__str__() """
    if self.stylized: return f"Stylized {self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
    return f"{self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
