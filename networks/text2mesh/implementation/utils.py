import os
import re
import shutil
import argparse

### Functions ###
def read_mesh(mesh_path):
    """
    Reads a 3d mesh and previews the result

    Inputs
        :mesh_path: <str> path to the mesh obj represnetation
    """
    with open(mesh_path, 'r', encoding='utf-8') as mesh_file:
        lines = mesh_file.read().splitlines()
        for i in range(len(lines)):
            if "f " in lines[i]: print(f"{i} {lines[i]}")

    
def check_mesh(mesh_path, text2mesh_path):
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

        if num_normals == 0: 
            raise ValueError(f"\033[91mFail: Could not determine number of vertex normals in {mesh_path}\033[0m")

        mesh_file.close()
        
        if num_vertices < num_normals: 
            print(f"\033[93mCaution[Obj Deprecated]: Number of verticies ({num_vertices}) < the number of normals ({num_normals})\033[0m")
            with open(f"{text2mesh_path}/mesh.py", 'r+') as text2mesh:
                text2mesh_content = text2mesh.read()
                updated_text2mesh = re.sub(r"self\.vertex_normals = mesh\.vertex_normals\.to\(device\)\.float\(\)", "self.vertex_normals = mesh.vertex_normals.to(device).float()[:self.vertices.shape[0], ::]", text2mesh_content)
                
                text2mesh.seek(0)
                text2mesh.truncate(0)
                text2mesh.write(updated_text2mesh + "\n# Edited line 29")
                text2mesh.close()

        if num_vertices > num_normals: raise ValueError(f"\033[91mFail[Obj Deprecated]: Number of verticies ({num_vertices}) > the number of normals ({num_normals})\033[0m")
        else: print(f"\033[92mSuccess[{mesh_path} is goo!]: Number of verticies ({num_vertices}) == the number of normals ({num_normals})\033[0m")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--mesh_path', type=str, default='/content/implementation/inputs/cat.obj')
    parser.add_argument('--text2mesh_path', type=str, default='/content/text2mesh')
    
    args = parser.parse_args()
    check_mesh(args.mesh_path, args.text2mesh_path)
    # read_mesh(args.mesh_path)