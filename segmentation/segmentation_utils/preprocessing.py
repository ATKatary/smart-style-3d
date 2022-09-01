import os
import trimesh
import pymeshlab
import numpy as np
from tqdm import tqdm

### Global Constants ####
colors = [[1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 0.8, 1, 1], [1, 0.1, 0.6, 1], [1, 0.647, 0, 1]]

def _npz_to_obj(npz, output_path, segment = False):
    """
    Converts an npz mesh into an obj mesh, if segmented then each segment is stored as a seperate obj file

    Inputs
        :npz: <np.ndarray | str> the mesh, if str then we will first read the file
        :output_path: <str> where to save the converted obj mesh, MUST NOT CONTAIN .obj or any extension
        :segment: <bool> indicating whether the npz object is segmented (default is False)
    
    Outputs
        :returns: <dict> containing the loaded npz data
    """
    if isinstance(npz, str):
        npz = np.load(npz, allow_pickle=True)
    if 'arr_0' in npz: data = dict(enumerate(npz['arr_0'].flatten(), 1))[1]
    else: data = dict(npz)

    vertices = data['vertices']
    faces = data['faces']

    mesh_set = pymeshlab.MeshSet()
    if segment: 
        labels = data['labels']
        print(f"This model has been segmented into {len(set(labels))} part(s)")
        
        indices_map = {}
        face_colors = np.ones((faces.shape[0], 4))
        vertex_colors = np.ones((vertices.shape[0], 4))
        vertex_indecies = {label: [] for label in set(labels)}

        for i, label in enumerate(labels): 
            vertex_indecies[label].append(i)
            vertex_colors[i] = np.array(colors[int(label)])

        
        for label, indices in vertex_indecies.items():
            faces_ = []
            for i in range(len(indices)): indices_map[indices[i]] = i
            
            print(f"Segmenting faces ....")
            for i in tqdm(range(len(faces))):
                v1, v2, v3 = faces[i]
                try:
                    faces_.append([indices_map[v1], indices_map[v2], indices_map[v3]])

                except: pass
                color_1 = labels[v1]
                color_2 = labels[v2]
                color_3 = labels[v3]
                if color_1 != color_2 or \
                color_2 != color_3 or \
                color_2 != color_3: color = colors[6]

                else: color = color_1

                face_colors[i] = color
            
            faces_ = np.array(faces_)
            vertices_ = np.array([vertices[i] for i in indices])
            try: mesh_set.add_mesh(pymeshlab.Mesh(vertices_, faces_))
            except: pass

        mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces, v_color_matrix=vertex_colors, f_color_matrix=face_colors))

    else: mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces))

    for i in range(len(mesh_set)):
        mesh_set.set_current_mesh(i)
        mesh_set.save_current_mesh(f"{output_path}_{i}.obj")

    print(f"Converted model(s) have been saved to {output_path}_*.obj")
    return data

def _obj_to_npz(obj_path, labels = None, output_path = None):
    """
    Converts an obj mesh to a npz object and stores the result if output_path is not None

    Inputs
        :obj_path: <str> path to where the obj object is stored
        :output_path: <str | None> where to store the converted npz file (default is None)
    
    Outputs
        :returns: <dict> representation of the converted obj file
    """
    mesh_set = pymeshlab.MeshSet()
    mesh_set.load_new_mesh(obj_path)

    mesh = mesh_set.current_mesh()

    faces = mesh.face_matrix()
    vertices = mesh.vertex_matrix()
    vertex_normals = mesh.vertex_normal_matrix()
    if labels is None: labels = np.zeros(vertices.shape[0])
    edges, _ = _prepare_edges_and_kdtree_with_vertices_faces(vertices, faces)

    if output_path: 
        head, tail = os.path.split(output_path)
        name, ext = os.path.splitext(tail)
        dataset_name = np.array([f"{name}".encode("utf8")])

        data_to_store = {"vertices": vertices, "faces": faces, "vertex_normals": vertex_normals, "edges": edges, "labels": labels, "dataset_name": dataset_name}
        np.savez(output_path, **data_to_store)

    return {"vertices": vertices, "faces": faces, "vertex_normals": vertex_normals, "labels": labels, "edges": edges}

def _prepare_edges_and_kdtree_with_vertices_faces(vertices, faces):
    vertices = vertices
    faces = faces
    edges = [set() for _ in range(vertices.shape[0])]
    for i in range(faces.shape[0]):
        for v in faces[i]:
            edges[v] |= set(faces[i])
    for i in range(vertices.shape[0]):
        if i in edges[i]:
            edges[i].remove(i)
        edges[i] = list(edges[i])
    max_vertex_degree = np.max([len(e) for e in edges])
    for i in range(vertices.shape[0]):
        if len(edges[i]) < max_vertex_degree:
            edges[i] += [-1] * (max_vertex_degree - len(edges[i]))
    edges = np.array(edges, dtype=np.int32)

    kdtree_query = []
    t_mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    n_nbrs = min(10, vertices.shape[0] - 2)
    for n in range(vertices.shape[0]):
        d, i_nbrs = t_mesh.kdtree.query(vertices[n], n_nbrs)
        i_nbrs_cleared = [inbr for inbr in i_nbrs if inbr != n and inbr < vertices.shape[0]]
        if len(i_nbrs_cleared) > n_nbrs - 1:
            i_nbrs_cleared = i_nbrs_cleared[:n_nbrs - 1]
        kdtree_query.append(np.array(i_nbrs_cleared, dtype=np.int32))
    kdtree_query = np.array(kdtree_query)
    assert kdtree_query.shape[1] == (n_nbrs - 1), 'Number of kdtree_query is wrong: ' + str(kdtree_query.shape[1])

    return edges, kdtree_query