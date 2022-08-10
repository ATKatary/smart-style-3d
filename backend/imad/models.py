"""
imad models
"""
import os
import uuid
from pathlib import Path
from django.db import models

### Global Constants ###
alphabet_size = 26
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
  stylized = models.BooleanField(default=False)
  faces = models.IntegerField(default=0)
  vertices = models.IntegerField(default=0)
  vertex_normals = models.IntegerField(default=0)
  name = models.CharField(max_length=alphabet_size, default="Vase")
  path = models.CharField(max_length=alphabet_size ** 2, default=f"{Path(__file__).parent.parent.parent.absolute()}/frontend/src/media/models/mesh.obj")
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

  def __str__(self) -> str:
    """ Override models.Model.__str__() """
    if self.stylized: return f"Stylized {self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
    return f"{self.name} mesh - v: {self.vertices} vn: {self.vertex_normals} f: {self.faces}"
