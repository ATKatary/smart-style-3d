import re
import os
import pymesh
import pymeshlab
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

### Global Constants ###
yes = {"yes", "yeah", "y", "yea"}

def _check_mesh(mesh_path, all_yes = False):
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
        
        if num_vertices != num_normals: 
            print(f"\033[93mCaution[{mesh_path} Deprecated]: Number of verticies ({num_vertices}) != the number of normals ({num_normals})\033[0m")
            if not all_yes: remesh = input("Do you want to remesh? (y, [n]): ")
            else: remesh = "y"
            if remesh.lower() in yes:
                print(f"Remeshing ...")
                ms = pymeshlab.MeshSet()
                ms.load_new_mesh(mesh_path)
                ms.meshing_isotropic_explicit_remeshing()
                ms.save_current_mesh(f"{mesh_path}")
                return _check_mesh(mesh_path)
            else:
                remove = input("Do you want to remove this model? (y, [n]): ")
                if remove in yes: os.remove(mesh_path)

        else: print(f"\033[92mSuccess[{mesh_path} is good!]: Number of verticies ({num_vertices}) == the number of normals ({num_normals})\033[0m")

def _subset(A, B):
    """ Checks A subset of B """
    for elm in A:
        if elm not in B: return False
    return True

def _plot(mesh, vertices, cog=False):
    fig = plt.figure(figsize=(4,4))
    ax = fig.add_subplot(111, projection='3d')
    for i in vertices: 
        x, y, z = mesh.vertices[i]
        ax.scatter(x, y, z) 
    if cog:
        ax.scatter(cog[0], cog[1], cog[2])
    plt.show()
    
def _save_modified_mesh(mesh, vertex_indicies, path):
    mesh_string = ""
    for i in range(mesh.vertices.shape[0]):
        if i in vertex_indicies:
            v = mesh.vertices[i]
            vn = mesh.vertex_normals[i]
            mesh_string += f"v {v[0]} {v[1]} {v[2]}\n"
            mesh_string += f"vn {vn[0]} {vn[1]} {vn[2]}\n"
    
    for v1, v2, v3 in mesh.faces:
        v1, v2, v3 = int(v1), int(v2), int(v3)
        for v in [v1, v2, v3]:
            if v not in vertex_indicies: break
        else:
            v1 = vertex_indicies.index(v1) + 1
            v2 = vertex_indicies.index(v2) + 1
            v3 = vertex_indicies.index(v3) + 1
            mesh_string += f"f {v1}//{v1} {v2}//{v2} {v3}//{v3}\n"

    # with open(mesh_path, "r") as f:
    #     for line in f.readlines():
    #         if line.startswith("f "):
    #             v1, v2, v3 = [int(v.split("//")[0]) - 1 for v in line.split(" ")[1:]]
    #             for v in [v1, v2, v3]:
    #                 if v not in vertex_indicies: break
    #             else:
    #                 v1 = vertex_indicies.index(v1) + 1
    #                 v2 = vertex_indicies.index(v2) + 1
    #                 v3 = vertex_indicies.index(v3) + 1
    #                 mesh_string += f"f {v1}//{v1} {v2}//{v2} {v3}//{v3}\n"
                    

    with open(path, "w") as f:
        f.write(mesh_string)

def _get_normal_to_vertices(mesh):
    # map from normal => all vertices with that normal
    normal_to_vertices = {}
    for i in range(mesh.vertex_normals.shape[0]):
        normal = mesh.vertex_normals[i].abs()
        x, y, z = normal
        normal = (float(x), float(y), float(z))
        if normal in normal_to_vertices:
            normal_to_vertices[normal].append(mesh.vertices[i])
        else:
            normal_to_vertices[normal] = [mesh.vertices[i]]
    
    # notfiy use of information
    i = 0
    for normal, vertices in normal_to_vertices.items():
        n = len(vertices)
        if n > 1:
            print(f"Normal {i} has {n} vertices along it")
        i += 1
    
    return normal_to_vertices

def _get_open_mesh(mesh, extremas, axes):
    open_mesh = []
    y_extremas = extremas[axes][0] + extremas[axes][1]
    for i in range(mesh.vertices.shape[0]):
        if i not in y_extremas: open_mesh.append(i) 
    return open_mesh

def _get_connected_components(mesh_path, mesh_dir):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)

    ms.generate_splitting_by_connected_components()
    print(f"I have found {len(ms)} connected components")
    for i in range(len(ms)):
        ms.set_current_mesh(i)
        ms.save_current_mesh(f"{mesh_dir}/component_{i}.obj")

def _get_edges(mesh):
    edges = []
    history = set()
    faces = list(map(lambda x: list(map(lambda y: int(y), x))[:3], mesh.faces))
    
    for v1, v2, v3 in tqdm(faces):
        edge1 = (v1, v2)
        edge2 = (v2, v3)
        edge3 = (v1, v3)
        if edge1 not in history: edges.append(edge1)
        if edge2 not in history: edges.append(edge2)
        if edge3 not in history: edges.append(edge3)
        history.add(edge1)
        history.add(edge2)
        history.add(edge3)
    edges = np.array(edges)
    print(f"Edges: {edges.shape[0]}")
    return edges

def _get_wire_network(mesh):
    edges = _get_edges(mesh)
    return pymesh.wires.WireNetwork.create_from_data(mesh.vertices, edges)

def _dist(a, b):
    """ Requires len(a) == len(b) """
    return sum([(a[i] - b[i]) ** 2 for i in range(len(a))]) ** 0.5
    
def _get_outer_layer(mesh, cog):
    """ Requires mesh.v == mesh.vn """
    outer = []
    inner = []
    
    vertices = list(map(lambda x: list(map(lambda y: float(y), x))[:3], mesh.vertices))
    vertex_normals = list(map(lambda x: list(map(lambda y: float(y), x))[:3], mesh.vertex_normals))
    
    for i in range(len(vertices)):
        v = vertices[i]
        vn = vertex_normals[i]

        a = _dist(v, vn)
        b = _dist(v, cog)
        c = _dist(vn, cog)
        theta = _law_of_cosine(a, b, c)

        if theta > np.pi / 2: outer.append(i)
        elif theta <= np.pi / 2: inner.append(i)
        else: print(f"Umm for some reason v == vn for vertex {i}")

    print(f"I found {len(outer)} vertices making the outer layer")
    print(f"I found {len(inner)} vertices making the inner layer")
    return outer, inner

def _get_cog(mesh):
    """ Find the center of gravity """
    x = float(mesh.vertices[:, 0].mean())
    y = float(mesh.vertices[:, 1].mean())
    z = float(mesh.vertices[:, 2].mean())
        
    return [x, y, z]

def _get_midpoint(a, b):
    """ Finds the midpoint of 2 vectors """
    return (a[:] + b[:]) / 2

def _law_of_cosine(a, b, c):
    return np.arccos((c**2 - b**2 - a**2) / (2 * a * b))

def _get_bases(mesh, e):
    """
    """
    shape = mesh.vertices.shape
    get_min = lambda c: mesh.vertices[:, c].min()
    get_max = lambda c: mesh.vertices[:, c].max()

    min_x, max_x = get_min(0), get_max(0)
    min_y, max_y = get_min(1), get_max(1)
    min_z, max_z = get_min(2), get_max(2)

    extremas = {"x": [[], []], "y": [[], []], "z": [[], []]}
    for i in range(mesh.vertices.shape[0]):
        vertex = mesh.vertices[i]
        x, y, z = vertex
        x, y, z = float(x), float(y), float(z)
        vertex = (x, y, z)
        if max_x - e <= x <= max_x: extremas["x"][0].append(i)
        if max_y - e <= y <= max_y: extremas["y"][0].append(i)
        if max_z - e <= x <= max_z: extremas["z"][0].append(i)
        
        if min_x <= x <= min_x + e: extremas["x"][1].append(i)
        if min_y <= y <= min_y + e: extremas["y"][1].append(i)
        if min_z <= z <= min_z + e: extremas["z"][1].append(i)

    # print out the extremeties
    try: 
        for axis, min_v, max_v in [("x", min_x, max_x), ("y", min_y, max_y), ("z", min_z, max_z)]:
            print(f">> min_{axis}: {min_v}")
            print(f">> max_{axis}: {max_v}\n")
    except: pass

    return extremas