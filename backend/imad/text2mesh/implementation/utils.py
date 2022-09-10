import os
import re
import shutil
import argparse
import pymeshlab 

remesh_command = lambda obj_path: f"python ../text2mesh/remesh.py --obj_path {obj_path}.obj"
    
### Functions ###
def check_mesh(mesh_path, i = 0):
    """
    Checks whether the number of verticies equals the number of vertex normals in a mesh and produces a warning or fails if they are not
    Changes the text2mesh mesh.py to reflect the discripency within the mesh file

    Inputs
        :mesh_path: <str> path to the mesh obj represnetation
        :text2mesh_path: <str> path to the text2mesh cloned repo

    Throws
        <ValueError> if the number of verticies > number of vertex normals
    """
    with open(mesh_path, 'r', encoding='utf-8') as mesh_file:
        mesh_file_content = mesh_file.read()
        num_vertices = len(re.findall("v .*", mesh_file_content))
        num_normals = len(re.findall("vn .*", mesh_file_content))
        
#         if num_normals == 0: 
#             raise ValueError(f"\033[91mFail: Could not determine number of vertex normals in {mesh_path}\033[0m")
        
        mesh_file.close()
        
        if num_vertices != num_normals: 
            if i == 0:   
                print(f"Remeshing {mesh_path} ...")
                ms = pymeshlab.MeshSet()

                ms.load_new_mesh(mesh_path)

                ms.meshing_isotropic_explicit_remeshing()

                ms.save_current_mesh(f"{mesh_path}")
                return check_mesh(mesh_path, i + 1)
        else: print(f"\033[92mSuccess[{mesh_path} is good!]: Number of verticies ({num_vertices}) == the number of normals ({num_normals})\033[0m")
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mesh_path', type=str, default='./inputs/cat.obj')
    parser.add_argument('--text2mesh_path', type=str, default='../text2mesh')

    args = parser.parse_args()
    check_mesh(args.mesh_path, args.text2mesh_path)