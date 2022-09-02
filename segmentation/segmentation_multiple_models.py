from tkinter import E
import pymeshlab
import numpy as np
from tqdm import tqdm
import pymesh
from segment import segment_mesh
import os


imad = "/home/ubuntu/imad"
models_dir = f"{imad}/segmentation/models/"
formative_dir = f"{imad}/formative_models_oriented/"
model_dir = f"{imad}/formative_models_oriented/reupload"

colors = [[1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 0.8, 1, 1], [1, 0.1, 0.6, 1], [1, 0.647, 0, 1], [0.5, 0.647, 0, 1], [1, 0.647, 0.5, 1], [0.5, 0.647, 0.5, 1], [0.5, 0.5, 0.2, 1], [0.1, 0.8, 0.1, 1], [0.9, 0.1, 0.5, 1], [0.2, 0.1, 0.9, 1], [0.8, 0.8, 0.1, 1], [0.843, 0.6423, 0.123, 1], [0.8123, 0.2423, 0.654, 1], [0.75, 0.63, 0.3, 1], [0.912, 0.36, 0.18, 1]]
too_many_faces = []
for i in range(64,100):
  mesh_path = f"{model_dir}/Model_{i}.obj"
  print(mesh_path)
  mesh_dir = f"{formative_dir}/model_{i}"
  # p_mesh = pymesh.load_mesh(mesh_path)
  # print(f'Working on {mesh_path}')
  # p_mesh, info = pymesh.remove_duplicated_faces(p_mesh)
  # p_mesh, info = pymesh.remove_isolated_vertices(p_mesh)
  # p_mesh, info = pymesh.remove_isolated_vertices(p_mesh)
  # pymesh.save_mesh(mesh_path, p_mesh)
  
  for fname in os.listdir(f"{formative_dir}/model_{i}/"):
    if fname.endswith('segmented.obj'):
        print(f"{i} already segmented\n")
        continue


  mesh_set = pymeshlab.MeshSet()
  mesh_set.load_new_mesh(mesh_path)
  # mesh_set.apply_coord_two_steps_smoothing()
  mesh_set.meshing_isotropic_explicit_remeshing(iterations=3)
  if(mesh_set.current_mesh().face_number() > 50000):
    too_many_faces.append(i)
    print('Skipping')
    with open("too_many_faces.txt", "a") as fi: 
      fi.write(str(i) + "\n")
    continue
  try: 
    labels = segment_mesh(mesh_set.current_mesh(),mesh_dir, k = 12)
    print("Got labels")
    with open("models_segmented.txt", "a") as fi: 
      fi.write(str(i) + "\n")

    mesh = mesh_set.current_mesh()
    faces = mesh.face_matrix()
    vertices = mesh.vertex_matrix()

    m = faces.shape[0]
    face_colors = np.zeros((m, 4))
    for i_n in tqdm(range(m)):
        face_colors[i_n] = colors[labels[i_n]]

    mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces, f_color_matrix=face_colors))
    print(f"{mesh_dir}/model_{i}_segmented_new.obj")
    mesh_set.save_current_mesh(f"{mesh_dir}/model_{i}_segmented_new.obj")
  except Exception as e: 
    print(E)
    print("Doesn't have enough i,j")
    with open("mesh_failure.txt", "a") as fi: 
      fi.write(str(i) + "\n")